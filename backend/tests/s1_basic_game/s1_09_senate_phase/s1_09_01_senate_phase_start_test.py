import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.senate_phase_start import SenatePhaseStartEffect
from rorapp.models import Game, Senator


@pytest.mark.django_db
def test_statesman_with_free_tribune_gets_status_at_senate_start(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.START
    game.save()
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.code = "22a"
    senator.statesman_name = "M. Porcius Cato the Elder"
    senator.location = "Rome"
    senator.save()

    # Act
    SenatePhaseStartEffect().execute(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.has_status_item(Senator.StatusItem.FREE_TRIBUNE)
