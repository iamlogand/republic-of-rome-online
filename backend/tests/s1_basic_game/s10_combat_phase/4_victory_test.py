import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Fleet, Game, Legion, War
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_land_victory_eliminates_war_and_reduces_unrest(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 2
    assert Campaign.objects.filter(game=game).exists() == False


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
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.popularity == 5
    assert commander.location == "Rome"


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
    resolver.casualty_order = []
    resolver.mortality_chits = []

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
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.location == "Rome"
    assert not commander.has_title(commander.Title.PROCONSUL)
