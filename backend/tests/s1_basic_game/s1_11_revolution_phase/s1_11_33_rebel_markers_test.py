from typing import Callable

import pytest
from rorapp.actions.contribute import ContributeAction
from rorapp.actions.declare_civil_war import DeclareCivilWarAction
from rorapp.actions.redistribute_talents import RedistributeTalentsAction
from rorapp.actions.transfer_talents import TransferTalentsAction
from rorapp.classes.concession import Concession
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Game, Senator


def _declare(campaign: Campaign, resolver: FakeRandomResolver) -> Game:
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    commander = campaign.commander
    assert commander is not None and commander.faction is not None
    DeclareCivilWarAction().execute(game.id, commander.faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)
    return game


@pytest.mark.django_db
def test_a_rebel_loses_his_knights_offices_and_concessions(
    land_victor: Campaign,
    settle_secondary_rebels: Callable[[Game], None],
    resolver: FakeRandomResolver,
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    commander.knights = 2
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.add_concession(Concession.MINING)
    commander.save()
    game = _declare(land_victor, resolver)

    # Act
    settle_secondary_rebels(game)

    # Assert
    commander.refresh_from_db()
    game.refresh_from_db()
    assert commander.knights == 0
    assert not commander.has_title(Senator.Title.FIELD_CONSUL)
    assert commander.concessions == []
    assert game.has_concession(Concession.MINING)


@pytest.mark.django_db
def test_a_rebel_keeps_his_faction_leader_marker(
    land_victor: Campaign,
    settle_secondary_rebels: Callable[[Game], None],
    resolver: FakeRandomResolver,
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    commander.add_title(Senator.Title.FACTION_LEADER)
    commander.save()
    game = _declare(land_victor, resolver)

    # Act
    settle_secondary_rebels(game)

    # Assert
    commander.refresh_from_db()
    assert commander.has_title(Senator.Title.FACTION_LEADER)


@pytest.mark.django_db
def test_a_rebel_earns_no_personal_revenue(
    land_victor: Campaign,
    settle_secondary_rebels: Callable[[Game], None],
    resolver: FakeRandomResolver,
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    game = _declare(land_victor, resolver)
    settle_secondary_rebels(game)

    # Act
    game.refresh_from_db()

    # Assert
    commander.refresh_from_db()
    assert game.phase == Game.Phase.REVENUE
    assert commander.talents == 0


@pytest.mark.django_db
def test_a_rebel_may_not_receive_talents_in_a_redistribution(
    land_victor: Campaign,
    settle_secondary_rebels: Callable[[Game], None],
    resolver: FakeRandomResolver,
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    game = _declare(land_victor, resolver)
    settle_secondary_rebels(game)
    faction = game.factions.get(position=1)
    senators = list(Senator.objects.filter(game=game, faction=faction).order_by("id"))
    total = sum(s.talents for s in senators) + faction.treasury
    allocation = {f"senator:{commander.id}": total}

    # Act
    result = RedistributeTalentsAction().execute(
        game.id, faction.id, {"Allocation": allocation}, resolver
    )

    # Assert
    assert result.success == False
    commander.refresh_from_db()
    assert commander.talents == 0


@pytest.mark.django_db
def test_a_rebel_may_not_be_sent_talents_by_another_faction(
    land_victor: Campaign,
    settle_secondary_rebels: Callable[[Game], None],
    resolver: FakeRandomResolver,
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    game = _declare(land_victor, resolver)
    settle_secondary_rebels(game)
    sender = Senator.objects.get(game=game, family_name="Manlius")
    sender.talents = 5
    sender.save()

    # Act
    result = TransferTalentsAction().execute(
        game.id,
        sender.faction_id,
        {
            "Sender": f"senator:{sender.id}",
            "Recipient": f"senator:{commander.id}",
            "Talents": "5",
        },
        resolver,
    )

    # Assert
    assert result.success == False
    commander.refresh_from_db()
    assert commander.talents == 0


@pytest.mark.django_db
def test_a_rebel_may_not_contribute_to_the_state(
    land_victor: Campaign,
    settle_secondary_rebels: Callable[[Game], None],
    resolver: FakeRandomResolver,
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    game = _declare(land_victor, resolver)
    settle_secondary_rebels(game)
    commander.refresh_from_db()
    commander.talents = 10
    commander.save()

    # Act
    result = ContributeAction().execute(
        game.id,
        commander.faction_id,
        {"Contributor": commander.id, "Talents": "10"},
        resolver,
    )

    # Assert
    assert result.success == False
    commander.refresh_from_db()
    assert commander.talents == 10
