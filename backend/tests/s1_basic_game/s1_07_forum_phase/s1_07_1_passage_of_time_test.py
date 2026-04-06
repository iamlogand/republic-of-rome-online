import pytest
from rorapp.classes.game_effect_item import GameEffect
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


@pytest.mark.django_db
def test_effects_are_cleared_at_start_of_forum_phase(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.START
    game.add_effect(GameEffect.MANPOWER_SHORTAGE)
    game.save()

    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.add_title(Senator.Title.HRAO)
    senator.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.effects == []
