import pytest
from rorapp.classes.game_effect_item import GameEffect
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game


@pytest.mark.django_db
def test_evil_omens_reduces_state_income_by_1T(revenue_game: Game):
    # Arrange
    game = revenue_game
    game.add_effect(GameEffect.EVIL_OMENS)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 299
