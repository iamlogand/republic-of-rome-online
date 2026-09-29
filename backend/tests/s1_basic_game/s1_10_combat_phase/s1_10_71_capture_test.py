from typing import List

import pytest
from rorapp.actions.pay_ransom import PayRansomAction
from rorapp.actions.redistribute_talents import RedistributeTalentsAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Game, Legion, Senator


def _setup_captive(game: Game, campaign: Campaign) -> Senator:
    captive = Senator.objects.get(game=game, family_name="Fabius")
    captive.captor = campaign.war
    captive.location = campaign.war.location
    captive.save()
    return captive


@pytest.mark.parametrize(
    "roll, chits, alive, captured",
    [
        (5, ["none", "1"], True, True),
        (5, ["1", "none"], False, False),
        (5, ["1"], False, False),
        (10, ["none", "1"], False, False),
    ],
)
@pytest.mark.django_db
def test_last_of_several_chits_captures_the_commander_unless_victorious(
    land_campaign: Campaign,
    resolver: FakeRandomResolver,
    roll: int,
    chits: List[str],
    alive: bool,
    captured: bool,
):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver.dice_rolls = [roll]
    resolver.mortality_chits = [chits]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander = Senator.objects.get(game=game, family_name="Cornelius")
    assert commander.alive == alive
    assert (commander.captor_id == land_campaign.war_id) == captured


@pytest.mark.django_db
def test_captive_leaves_his_forces_on_the_war(
    land_campaign: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver.dice_rolls = [5]
    resolver.mortality_chits = [["none", "1"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    campaign = Campaign.objects.get(id=land_campaign.id)
    assert campaign.commander is None
    assert Legion.objects.filter(campaign=campaign).count() == 6


@pytest.mark.django_db
def test_captive_keeps_his_office_and_does_not_become_proconsul(
    land_campaign: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver.dice_rolls = [5]
    resolver.mortality_chits = [["none", "1"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander = Senator.objects.get(game=game, family_name="Cornelius")
    assert commander.has_title(Senator.Title.FIELD_CONSUL)
    assert not commander.has_title(Senator.Title.PROCONSUL)


@pytest.mark.django_db
def test_master_of_horse_returns_to_rome_when_the_dictator_is_captured(
    land_campaign: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_campaign.game
    dictator = land_campaign.commander
    assert dictator is not None
    dictator.clear_titles()
    dictator.add_title(Senator.Title.DICTATOR)
    dictator.save()
    master_of_horse = Senator.objects.get(game=game, family_name="Fabius")
    master_of_horse.add_title(Senator.Title.MASTER_OF_HORSE)
    master_of_horse.location = land_campaign.war.location
    master_of_horse.save()
    land_campaign.master_of_horse = master_of_horse
    land_campaign.save()
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver.dice_rolls = [5]
    resolver.mortality_chits = [["none", "1"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    master_of_horse.refresh_from_db()
    assert master_of_horse.location == "Rome"
    assert master_of_horse.has_title(Senator.Title.MASTER_OF_HORSE)


@pytest.mark.django_db
def test_captives_are_killed_when_their_war_is_defeated(
    land_campaign: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_campaign.game
    captive = _setup_captive(game, land_campaign)
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    captive.refresh_from_db()
    assert captive.alive == False


@pytest.mark.django_db
def test_captive_earns_no_personal_revenue(
    land_campaign: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_campaign.game
    captive = _setup_captive(game, land_campaign)
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.START
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    captive.refresh_from_db()
    assert captive.talents == 0


@pytest.mark.django_db
def test_captive_talents_are_left_out_of_redistribution(
    land_campaign: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_campaign.game
    captive = _setup_captive(game, land_campaign)
    captive.talents = 7
    captive.save()
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.REDISTRIBUTION
    game.save()
    assert captive.faction_id is not None
    allocation = {f"senator:{captive.id}": 0, "faction_treasury": 7}

    # Act
    result = RedistributeTalentsAction().execute(
        game.id, captive.faction_id, {"Allocation": allocation}, resolver
    )

    # Assert
    captive.refresh_from_db()
    assert not result.success
    assert captive.talents == 7


@pytest.mark.django_db
def test_paying_ransom_returns_the_captive_to_rome(
    land_campaign: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_campaign.game
    captive = _setup_captive(game, land_campaign)
    captive.talents = 4
    captive.save()
    faction = captive.faction
    assert faction is not None
    faction.treasury = 10
    faction.save()

    # Act
    result = PayRansomAction().execute(
        game.id,
        faction.id,
        {"Captive": captive.id, "Talents from the faction treasury": 6},
        resolver,
    )

    # Assert
    captive.refresh_from_db()
    faction.refresh_from_db()
    assert result.success
    assert captive.captor is None
    assert captive.location == "Rome"
    assert captive.talents == 0
    assert faction.treasury == 4


@pytest.mark.parametrize(
    "talents, treasury, from_treasury, success",
    [
        (10, 0, 0, True),
        (4, 10, 5, False),
        (20, 3, 5, False),
    ],
)
@pytest.mark.django_db
def test_ransom_is_paid_in_full_from_the_captive_and_faction_treasuries(
    land_campaign: Campaign,
    resolver: FakeRandomResolver,
    talents: int,
    treasury: int,
    from_treasury: int,
    success: bool,
):
    # Arrange
    game = land_campaign.game
    captive = _setup_captive(game, land_campaign)
    captive.talents = talents
    captive.save()
    faction = captive.faction
    assert faction is not None
    faction.treasury = treasury
    faction.save()

    # Act
    result = PayRansomAction().execute(
        game.id,
        faction.id,
        {"Captive": captive.id, "Talents from the faction treasury": from_treasury},
        resolver,
    )

    # Assert
    captive.refresh_from_db()
    assert result.success == success
    assert captive.captive != success
