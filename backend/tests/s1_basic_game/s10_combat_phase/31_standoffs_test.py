import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Fleet, Game, Legion
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_land_standoff_reduces_forces_and_keeps_campaign(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [15]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game).count() == 7
    assert Campaign.objects.filter(game=game).exists() == True
    game.refresh_from_db()
    assert game.unrest == 3


@pytest.mark.django_db
def test_naval_standoff_reduces_fleets_and_keeps_campaign(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [11]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Fleet.objects.filter(game=game).count() == 7
    assert Campaign.objects.filter(game=game).exists() == True
