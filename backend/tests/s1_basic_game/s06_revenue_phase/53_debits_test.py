import pytest
from rorapp.models import Fleet, Game, Legion, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_state_revenue_reduced_by_active_war_cost(revenue_game: Game):
    # Arrange
    game = revenue_game
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
        location="Macedonia",
        status=War.Status.ACTIVE,
    )

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 260


@pytest.mark.django_db
def test_state_revenue_reduced_by_legion_maintenance(revenue_game: Game):
    # Arrange
    game = revenue_game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i)

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 280


@pytest.mark.django_db
def test_state_revenue_reduced_by_fleet_maintenance(revenue_game: Game):
    # Arrange
    game = revenue_game
    for i in range(1, 6):
        Fleet.objects.create(game=game, number=i)

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 290
