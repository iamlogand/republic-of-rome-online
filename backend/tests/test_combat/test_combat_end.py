import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Game, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_naval_victory_with_all_fleets_lost_not_unprosecuted(basic_game: Game):
    """When a naval battle was won but all fleets were lost, war should NOT be marked unprosecuted."""

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
        naval_strength=0,  # Already zeroed — naval battle was won
        fought_naval_battle=True,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )

    random_resolver = FakeRandomResolver()
    random_resolver.dice_rolls = []
    random_resolver.casualty_order = []
    random_resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, random_resolver)

    # Assert
    war.refresh_from_db()
    assert war.unprosecuted == False
