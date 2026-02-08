import pytest
from rorapp.classes.concession import Concession
from rorapp.helpers.kill_senator import kill_senator
from rorapp.models import Game, Senator


@pytest.mark.django_db
def test_kill_senator_releases_concessions_to_game(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.MORTALITY
    game.sub_phase = Game.SubPhase.START
    game.save()

    senator = Senator.objects.get(game=game, name="Cornelius")
    senator.add_concession(Concession.MINING)
    senator.add_concession(Concession.LATIUM_TAX_FARMER)
    senator.save()

    # Act
    kill_senator(game.id, senator.id)

    # Assert
    game.refresh_from_db()
    assert "Mining" in game.concessions
    assert "Latium Tax Farmer" in game.concessions

    senator.refresh_from_db()
    assert senator.concessions == []

    expected_message = "The death of Cornelius has made the Mining and Latium Tax Farmer concessions available."
    assert game.logs.filter(text=expected_message).count() == 1
