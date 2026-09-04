import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_land_victory_eliminates_war_and_reduces_unrest(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 2
    assert War.objects.filter(game=game).exists() == False


@pytest.mark.django_db
def test_land_victory_commander_gains_popularity(land_campaign: Campaign):
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
    commander.refresh_from_db()
    assert commander.popularity == 5
    assert commander.location == "Cisalpine Gaul"


@pytest.mark.django_db
def test_naval_victory_reduces_unrest(naval_campaign: Campaign):
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
    game.refresh_from_db()
    assert game.unrest == 2


@pytest.mark.django_db
def test_naval_victory_fleet_only_commander_returns_to_rome(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.location == "Rome"
    assert not commander.has_title(commander.Title.PROCONSUL)


@pytest.mark.django_db
def test_land_victor_keeps_his_army_in_the_field(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    land_campaign.refresh_from_db()
    assert land_campaign.land_victory == True
    assert land_campaign.war is None
    assert Legion.objects.filter(game=game, campaign=land_campaign).count() == 10


@pytest.mark.django_db
def test_land_victor_who_dies_returns_his_force_to_the_reserve(
    land_campaign: Campaign,
):
    # Arrange
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [16]
    resolver.mortality_chits = [[commander.code]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.alive == False
    assert Campaign.objects.filter(game=game).exists() == False
    assert Legion.objects.filter(game=game, campaign__isnull=False).count() == 0


@pytest.mark.django_db
def test_other_commander_on_the_war_returns_to_rome(two_campaigns):
    # Arrange
    campaign1, campaign2 = two_campaigns
    game = campaign1.game
    commander1 = campaign1.commander
    commander2 = campaign2.commander
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=campaign1)
    for i in range(11, 21):
        Legion.objects.create(game=game, number=i, campaign=campaign2)
    commander1.add_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
    commander1.save()
    for faction in game.factions.all():
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18, 18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander2.refresh_from_db()
    assert commander2.location == "Rome"
    assert Campaign.objects.filter(game=game).count() == 1
    commander1.refresh_from_db()
    assert commander1.location == "Cisalpine Gaul"
