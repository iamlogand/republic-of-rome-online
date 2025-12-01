import pytest
from rorapp.models import Fleet, Game, Legion, Log, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_state_revenue(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.START
    game.state_treasury = 200
    game.save()

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    assert game.state_treasury == 300
    expected_message = "The State earned 100T of revenue."
    assert game.logs.filter(text=expected_message).count() == 1


@pytest.mark.django_db
def test_state_revenue_with_debits(basic_game: Game):

    # Arrange
    game = basic_game
    game.phase = Game.Phase.REVENUE
    game.sub_phase = Game.SubPhase.START
    game.state_treasury = 200
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
        status=War.Status.INACTIVE,
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

    for i in range(1, 11):
        Legion.objects.create(game=game, number=i)

    for i in range(1, 6):
        Fleet.objects.create(game=game, number=i)

    # Act
    execute_effects_and_manage_actions(game.id)

    # Assert
    game.refresh_from_db()
    # 200T base + 100T revenue - 40T active wars - 20T legions - 10T fleets = 230T
    assert game.state_treasury == 230
    expected_message = "The State earned 100T of revenue and spent 40T on 2 active wars, 20T on maintaining 10 legions and 10T on maintaining 5 fleets."
    assert game.logs.filter(text=expected_message).count() == 1
