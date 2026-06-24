import pytest
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game


@pytest.mark.django_db
def test_drought_increases_unrest_in_population_phase(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.POPULATION
    game.sub_phase = Game.SubPhase.START
    game.add_effect(GameEffect.DROUGHT)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 1


@pytest.mark.django_db
def test_multiple_drought_effects_each_increase_unrest(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.POPULATION
    game.sub_phase = Game.SubPhase.START
    game.add_effect(GameEffect.DROUGHT)
    game.add_effect(GameEffect.DROUGHT)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 2
