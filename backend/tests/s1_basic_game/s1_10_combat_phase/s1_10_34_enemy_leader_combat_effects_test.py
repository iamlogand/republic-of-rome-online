import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, EnemyLeader, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


def _setup_land_campaign(
    game: Game,
    series_name: str,
    land_strength: int,
    disaster_numbers=None,
    standoff_numbers=None,
) -> Campaign:
    game.phase = Game.Phase.COMBAT
    game.sub_phase = Game.SubPhase.START
    game.save()

    war = War.objects.create(
        game=game,
        name="Test War",
        series_name=series_name,
        index=0,
        land_strength=land_strength,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=disaster_numbers or [],
        standoff_numbers=standoff_numbers or [],
        spoils=20,
        location="Test",
        status=War.Status.ACTIVE,
    )

    commander = Senator.objects.get(game=game, family_name="Cornelius")
    commander.add_title(Senator.Title.FIELD_CONSUL)
    commander.location = war.location
    commander.save()

    return Campaign.objects.create(game=game, war=war, commander=commander)


@pytest.mark.django_db
def test_active_leader_strength_adds_to_war_negative_modifier(basic_game: Game):
    # Arrange
    campaign = _setup_land_campaign(
        basic_game, series_name="TestSeries", land_strength=2
    )
    game = campaign.game
    EnemyLeader.objects.create(
        game=game,
        name="Test Leader",
        series_name="TestSeries",
        strength=5,
        disaster_number=99,
        standoff_number=99,
        active=True,
    )
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [3]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert War.objects.filter(game=game, name="Test War").exists()


@pytest.mark.django_db
def test_active_leader_disaster_number_triggers_automatic_disaster(basic_game: Game):
    # Arrange
    campaign = _setup_land_campaign(
        basic_game, series_name="TestSeries", land_strength=20
    )
    game = campaign.game
    EnemyLeader.objects.create(
        game=game,
        name="Test Leader",
        series_name="TestSeries",
        strength=0,
        disaster_number=7,
        standoff_number=99,
        active=True,
    )
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [7]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game).count() == 5  # (10 + 1) // 2 = 5 losses


@pytest.mark.django_db
def test_active_leader_standoff_number_triggers_automatic_standoff(basic_game: Game):
    # Arrange
    campaign = _setup_land_campaign(
        basic_game, series_name="TestSeries", land_strength=20
    )
    game = campaign.game
    EnemyLeader.objects.create(
        game=game,
        name="Test Leader",
        series_name="TestSeries",
        strength=0,
        disaster_number=99,
        standoff_number=7,
        active=True,
    )
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [7]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game).count() == 7  # (10 + 3) // 4 = 3 losses


@pytest.mark.django_db
def test_leader_disaster_is_independent_of_war_disaster(basic_game: Game):
    # Arrange
    campaign = _setup_land_campaign(
        basic_game, series_name="TestSeries", land_strength=20, disaster_numbers=[10]
    )
    game = campaign.game
    EnemyLeader.objects.create(
        game=game,
        name="Test Leader",
        series_name="TestSeries",
        strength=0,
        disaster_number=9,
        standoff_number=99,
        active=True,
    )
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [9]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert (
        Legion.objects.filter(game=game).count() == 5
    )  # disaster: (10 + 1) // 2 = 5 losses


@pytest.mark.django_db
def test_leader_deactivates_when_last_matching_war_is_defeated(basic_game: Game):
    # Arrange
    campaign = _setup_land_campaign(
        basic_game, series_name="TestSeries", land_strength=3
    )
    game = campaign.game
    leader = EnemyLeader.objects.create(
        game=game,
        name="Test Leader",
        series_name="TestSeries",
        strength=0,
        disaster_number=99,
        standoff_number=99,
        active=True,
    )
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [3]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader.refresh_from_db()
    assert leader.active is False


@pytest.mark.django_db
def test_leader_stays_active_when_other_matching_war_still_exists(basic_game: Game):
    # Arrange
    campaign = _setup_land_campaign(
        basic_game, series_name="TestSeries", land_strength=3
    )
    game = campaign.game
    War.objects.create(
        game=game,
        name="Test War 2",
        series_name="TestSeries",
        index=1,
        land_strength=3,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[],
        standoff_numbers=[],
        spoils=20,
        location="Test",
        status=War.Status.ACTIVE,
    )
    leader = EnemyLeader.objects.create(
        game=game,
        name="Test Leader",
        series_name="TestSeries",
        strength=0,
        disaster_number=99,
        standoff_number=99,
        active=True,
    )
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [6]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    leader.refresh_from_db()
    assert leader.active is True
