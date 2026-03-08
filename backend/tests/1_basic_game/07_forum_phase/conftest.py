import pytest
from rorapp.models import Game


@pytest.fixture
def forum_game(basic_game: Game) -> Game:
    game = basic_game
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
    game.save()
    return game
