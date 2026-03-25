import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_major_corrupt_marker_assigned_at_senate_start(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.START
    game.save()

    senators = list(Senator.objects.filter(game=game, alive=True))
    julius = senators[0]
    julius.add_title(Senator.Title.ROME_CONSUL)
    julius.add_title(Senator.Title.HRAO)
    julius.location = "Rome"
    julius.save()

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    julius.refresh_from_db()
    assert julius.has_status_item(Senator.StatusItem.MAJOR_CORRUPT)
