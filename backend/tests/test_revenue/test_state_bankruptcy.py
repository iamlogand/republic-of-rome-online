import pytest
from rorapp.models import Game
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_state_bankruptcy(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.MORTALITY
    game.sub_phase = Game.SubPhase.START
    game.state_treasury = -100
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is not None
    assert game.phase == Game.Phase.MORTALITY  # Confirm other effects haven't executed
    assert game.sub_phase == Game.SubPhase.START
    expected_text_start = "Game over! The State Treasury fell into bankruptcy"
    assert game.logs.order_by("created_on").last().text.startswith(expected_text_start)
