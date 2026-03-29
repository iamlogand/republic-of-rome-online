import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import EnemyLeader, Game, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_senator_killed_by_matching_mortality_chit(
    mortality_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = mortality_game
    senator = Senator.objects.create(
        game=game,
        family_name="TestUnaligned",
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


@pytest.mark.django_db
def test_imminent_war_becomes_active_at_turn_start(
    mortality_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = mortality_game
    war = War.objects.create(
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
        status=War.Status.IMMINENT,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war.refresh_from_db()
    assert war.status == War.Status.ACTIVE


@pytest.mark.django_db
def test_imminent_war_activation_also_activates_inactive_leader(
    mortality_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = mortality_game
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
        status=War.Status.IMMINENT,
    )
    leader = EnemyLeader.objects.create(
        game=game,
        name="Hamilcar",
        series_name="Punic",
        strength=3,
        disaster_number=8,
        standoff_number=12,
        active=False,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader.refresh_from_db()
    assert leader.active is True


@pytest.mark.django_db
def test_imminent_war_activation_does_not_affect_already_active_leader(
    mortality_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = mortality_game
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
        status=War.Status.IMMINENT,
    )
    leader = EnemyLeader.objects.create(
        game=game,
        name="Hamilcar",
        series_name="Punic",
        strength=3,
        disaster_number=8,
        standoff_number=12,
        active=True,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader.refresh_from_db()
    assert leader.active is True


@pytest.mark.django_db
def test_only_one_imminent_war_per_series_activates_per_turn(
    mortality_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = mortality_game
    war1 = War.objects.create(
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
        status=War.Status.IMMINENT,
    )
    war2 = War.objects.create(
        game=game,
        name="2nd Punic War",
        series_name="Punic",
        index=1,
        land_strength=15,
        fleet_support=5,
        naval_strength=0,
        disaster_numbers=[10],
        standoff_numbers=[11, 15],
        spoils=25,
        location="Italia",
        status=War.Status.IMMINENT,
    )

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war1.refresh_from_db()
    assert war1.status == War.Status.ACTIVE
    war2.refresh_from_db()
    assert war2.status == War.Status.IMMINENT
