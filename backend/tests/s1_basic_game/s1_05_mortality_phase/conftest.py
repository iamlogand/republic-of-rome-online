import pytest
from rorapp.models import Game


@pytest.fixture
def mortality_game(basic_game: Game) -> Game:
    game = basic_game
    game.phase = Game.Phase.MORTALITY
    game.sub_phase = Game.SubPhase.START
    game.save()
    return game
