import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Game, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_naval_victory_with_all_fleets_lost_not_unprosecuted(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    game.save()

    war = War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=0,
        fought_naval_battle=True,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )

    resolver = FakeRandomResolver()
    resolver.dice_rolls = []
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war.refresh_from_db()
    assert war.unprosecuted == False
