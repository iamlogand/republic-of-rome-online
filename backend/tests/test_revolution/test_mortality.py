import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Game, Senator
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_unaligned_senator_killed_by_mortality_chit(basic_game: Game):
    """An unaligned senator (faction=None) should be killed by a matching mortality chit."""

    game = basic_game
    game.phase = Game.Phase.MORTALITY
    game.sub_phase = Game.SubPhase.START
    game.save()

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

    random_resolver = FakeRandomResolver()
    random_resolver.mortality_chits = ["99"]
    random_resolver.dice_rolls = []
    random_resolver.casualty_order = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    senator.refresh_from_db()
    assert senator.alive == False
