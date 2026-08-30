import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Fleet, Legion
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_land_victory_creates_one_veteran_owing_allegiance_to_commander(
    land_campaign: Campaign,
):
    # Arrange
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    veteran = Legion.objects.get(game=game, veteran=True)
    assert veteran.allegiance == commander


@pytest.mark.django_db
def test_land_stalemate_creates_veteran(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [5]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game, veteran=True).count() == 1


@pytest.mark.django_db
def test_land_standoff_creates_veteran(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [15]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game, veteran=True).count() == 1


@pytest.mark.django_db
def test_land_disaster_creates_no_veteran(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game, veteran=True).exists() == False


@pytest.mark.django_db
def test_land_defeat_creates_no_veteran(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 7):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [4]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game).count() == 2
    assert Legion.objects.filter(game=game, veteran=True).exists() == False


@pytest.mark.django_db
def test_naval_victory_creates_no_veteran(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    for i in range(1, 6):
        Legion.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game, veteran=True).exists() == False


@pytest.mark.django_db
def test_only_a_non_veteran_survivor_is_promoted(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    Legion.objects.create(game=game, number=1, campaign=land_campaign, veteran=True)
    for i in range(2, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game, veteran=True).count() == 2
    promoted = Legion.objects.get(game=game, allegiance__isnull=False)
    assert promoted.number == 2


@pytest.mark.django_db
def test_no_veteran_is_created_when_every_survivor_is_already_a_veteran(
    land_campaign: Campaign,
):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign, veteran=True)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game, veteran=True).count() == 10
    assert Legion.objects.filter(game=game, allegiance__isnull=False).exists() == False


@pytest.mark.django_db
def test_promoted_legion_follows_the_resolver_selection(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]
    resolver.veteran_order = ["V"]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.get(game=game, veteran=True).number == 5


@pytest.mark.django_db
def test_veteran_created_by_a_dead_commander_owes_allegiance_to_nobody(
    land_campaign: Campaign,
):
    # Arrange
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [5]
    resolver.mortality_chits = [["1"]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.alive == False
    veteran = Legion.objects.get(game=game, veteran=True)
    assert veteran.allegiance is None


@pytest.mark.django_db
def test_allegiance_is_released_when_the_owning_senator_dies(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None
    commander.family = False
    commander.save()
    for i in range(1, 7):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    reserve_veteran = Legion.objects.create(
        game=game, number=7, veteran=True, allegiance=commander
    )
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [4]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    reserve_veteran.refresh_from_db()
    assert reserve_veteran.veteran == True
    assert reserve_veteran.allegiance is None
