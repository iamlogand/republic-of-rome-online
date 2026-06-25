import pytest
from rorapp.classes.game_effect_item import GameEffect
from rorapp.models import Game
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_allied_enthusiasm_grants_50T_to_state(revenue_game: Game):
    # Arrange
    game = revenue_game
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 350  # 200 + 100 base + 50 enthusiasm


@pytest.mark.django_db
def test_extreme_allied_enthusiasm_grants_75T_to_state(revenue_game: Game):
    # Arrange
    game = revenue_game
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 375  # 200 + 100 base + 75 enthusiasm


@pytest.mark.django_db
def test_allied_enthusiasm_effect_removed_after_revenue(revenue_game: Game):
    # Arrange
    game = revenue_game
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 0
