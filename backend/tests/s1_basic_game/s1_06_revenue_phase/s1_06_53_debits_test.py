import pytest
from rorapp.classes.concession import Concession
from rorapp.classes.game_effect_item import GameEffect
from rorapp.models import Fleet, Game, Legion, Senator, War
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


@pytest.mark.django_db
def test_state_revenue_reduced_by_type_i_land_bill(revenue_game: Game):
    # Arrange
    game = revenue_game
    game.add_effect(GameEffect.LAND_BILL_1)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 280


@pytest.mark.django_db
def test_type_i_land_bill_marker_removed_after_payment(revenue_game: Game):
    # Arrange
    game = revenue_game
    game.add_effect(GameEffect.LAND_BILL_1)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.LAND_BILL_1) == 0


@pytest.mark.django_db
def test_type_ii_land_bill_marker_not_removed_after_payment(revenue_game: Game):
    # Arrange
    game = revenue_game
    game.add_effect(GameEffect.LAND_BILL_2)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.LAND_BILL_2) == 1


@pytest.mark.django_db
def test_state_revenue_reduced_by_type_ii_and_iii_land_bills(revenue_game: Game):
    # Arrange
    game = revenue_game
    game.add_effect(GameEffect.LAND_BILL_2)
    game.add_effect(GameEffect.LAND_BILL_3)
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 285  # 200 + 100 - 5 - 10


@pytest.mark.django_db
def test_land_commissioner_earns_revenue(revenue_game: Game):
    # Arrange
    game = revenue_game
    senator = Senator.objects.filter(game=game, alive=True).first()
    assert senator is not None
    senator.add_concession(Concession.LAND_COMMISSIONER)
    senator.save()
    initial_talents = senator.talents

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert - senator earns 1T base + 3T from land commissioner
    senator.refresh_from_db()
    assert senator.talents == initial_talents + 4
