import pytest
from rorapp.models import Game, Senator


@pytest.fixture
def population_game(basic_game: Game):
    game = basic_game
    game.phase = Game.Phase.POPULATION
    game.sub_phase = Game.SubPhase.STATE_OF_REPUBLIC_SPEECH
    game.unrest = 0
    game.save()
    senator = Senator.objects.filter(
        game=game, alive=True, faction__isnull=False
    ).first()
    assert senator
    senator.add_title(Senator.Title.HRAO)
    senator.popularity = 0
    senator.save()
    return game
