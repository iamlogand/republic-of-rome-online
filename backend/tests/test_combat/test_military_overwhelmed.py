import pytest
from rorapp.models import Game, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_military_overwhelmed(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    game.save()
    
    War.objects.create(
        game=game,
        name="1st Punic War",
        series_name="Punic",
        index=0,
        land_strength=10,
        fleet_support=5,
        naval_strength=10,
        disaster_numbers=[13],
        standoff_numbers=[11, 14],
        spoils=35,
        location="Sicilia",
        status=War.Status.ACTIVE,
    )
    War.objects.create(
        game=game,
        name="1st Gallic War",
        series_name="Gallic",
        index=0,
        land_strength=10,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[13],
        standoff_numbers=[15],
        spoils=20,
        location="Cisalpine Gaul",
        status=War.Status.ACTIVE,
    )
    War.objects.create(
        game=game,
        name="1st Macedonian War",
        series_name="Macedonian",
        index=0,
        land_strength=12,
        fleet_support=10,
        naval_strength=0,
        disaster_numbers=[12],
        standoff_numbers=[11, 18],
        spoils=25,
        location="Macedonian",
        status=War.Status.ACTIVE,
    )
    War.objects.create(
        game=game,
        name="1st Illyrian War",
        series_name="Illyrian",
        index=0,
        land_strength=5,
        fleet_support=3,
        naval_strength=0,
        disaster_numbers=[5],
        standoff_numbers=[17],
        spoils=10,
        location="Illyricum",
        status=War.Status.ACTIVE,
    )

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is not None
    assert game.phase == Game.Phase.COMBAT  # Confirm other effects haven't executed
    assert game.sub_phase == Game.SubPhase.END
    expected_text_start = "Game over! The military was overwhelmed by 4 simultaneous wars"
    assert game.logs.order_by("created_on").last().text.startswith(expected_text_start)
