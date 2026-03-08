import pytest
from rorapp.models import Game, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_state_bankruptcy_ends_game(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.MORTALITY
    game.sub_phase = Game.SubPhase.START
    game.state_treasury = -100
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is not None


@pytest.mark.django_db
def test_military_overwhelmed_ends_game(basic_game: Game):
    # Arrange
    game = basic_game
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.END
    game.save()

    for name, location in [
        ("1st Punic War", "Sicilia"),
        ("1st Gallic War", "Cisalpine Gaul"),
        ("1st Macedonian War", "Macedonia"),
        ("1st Illyrian War", "Illyricum"),
    ]:
        War.objects.create(
            game=game,
            name=name,
            series_name=name.split()[1],
            index=0,
            land_strength=10,
            fleet_support=0,
            naval_strength=0,
            disaster_numbers=[],
            standoff_numbers=[],
            spoils=10,
            location=location,
            status=War.Status.ACTIVE,
        )

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is not None
