import pytest
from rorapp.actions.declare_revolt import DeclareRevoltAction
from rorapp.classes.concession import Concession
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Game, Log, Senator

pytestmark = pytest.mark.usefixtures("civil_war_flag")


def _declare_and_end_phase(campaign: Campaign, resolver: FakeRandomResolver) -> Senator:
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    rebel = campaign.commander
    assert rebel is not None and rebel.faction_id is not None
    DeclareRevoltAction().execute(game.id, rebel.faction_id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)
    rebel.refresh_from_db()
    return rebel


@pytest.mark.django_db
def test_rebel_returns_his_concessions(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    commander.add_concession(Concession.MINING)
    commander.add_concession(Concession.HARBOR_FEES)
    commander.save()

    # Act
    rebel = _declare_and_end_phase(land_victor, resolver)

    # Assert
    assert rebel.get_concessions() == []
    game = Game.objects.get(id=rebel.game_id)
    assert Concession.MINING.value in game.available_concessions
    assert Concession.HARBOR_FEES.value in game.available_concessions
    assert Log.objects.filter(
        game=game,
        text="Cornelius forfeited the mining and harbor fees concessions.",
    ).exists()


@pytest.mark.django_db
def test_rebel_loses_his_knights(land_victor: Campaign, resolver: FakeRandomResolver):
    # Arrange
    commander = land_victor.commander
    assert commander is not None
    commander.knights = 3
    commander.save()

    # Act
    rebel = _declare_and_end_phase(land_victor, resolver)

    # Assert
    assert rebel.knights == 0
    assert Log.objects.filter(
        game=rebel.game_id, text="Cornelius forfeited his 3 knights."
    ).exists()


@pytest.mark.django_db
def test_rebel_earns_no_personal_revenue(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.START
    game.save()
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    rebel.rebel = True
    rebel.add_concession(Concession.MINING)
    rebel.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    rebel.refresh_from_db()
    assert rebel.talents == 0
