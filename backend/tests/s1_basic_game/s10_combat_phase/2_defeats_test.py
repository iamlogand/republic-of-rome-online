import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Game, Legion, Fleet
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_land_defeat_kills_commander_and_raises_unrest(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    commander = land_campaign.commander
    assert commander is not None
    for i in range(1, 7):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [4]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.alive == False
    game.refresh_from_db()
    assert game.unrest == 5


@pytest.mark.django_db
def test_land_total_defeat_eliminates_campaign(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 7):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [3]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game).count() == 0
    assert Campaign.objects.filter(game=game).exists() == False


@pytest.mark.django_db
def test_naval_defeat_kills_commander_and_raises_unrest(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [3]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.alive == False
    game.refresh_from_db()
    assert game.unrest == 5


@pytest.mark.django_db
def test_naval_total_defeat_eliminates_campaign(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    for i in range(1, 6):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [1]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Fleet.objects.filter(game=game).count() == 0
    assert Campaign.objects.filter(game=game).exists() == False
