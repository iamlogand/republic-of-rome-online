import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_senator_killed_by_matching_mortality_chit(mortality_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = mortality_game
    senator = Senator.objects.create(
        game=game,
        name="TestUnaligned",
        code="99",
        faction=None,
        alive=True,
        military=1,
        oratory=1,
        loyalty=7,
        influence=1,
    )
    resolver.mortality_chits = ["99"]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.alive == False
