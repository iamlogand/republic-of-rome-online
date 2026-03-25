import pytest
from rorapp.models import Game


@pytest.fixture
def revenue_game(basic_game: Game) -> Game:
    game = basic_game
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.START
    game.state_treasury = 200
    game.save()
    return game
