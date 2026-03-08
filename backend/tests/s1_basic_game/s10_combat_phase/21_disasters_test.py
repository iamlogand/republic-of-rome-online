import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import Campaign, Fleet, Game, Legion
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions


@pytest.mark.django_db
def test_land_disaster_halves_forces_and_raises_unrest(land_campaign: Campaign):
    # Arrange
    game = land_campaign.game
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=land_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [13]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game).count() == 5
    game.refresh_from_db()
    assert game.unrest == 4


@pytest.mark.django_db
def test_naval_disaster_halves_fleets_and_raises_unrest(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [13]
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Fleet.objects.filter(game=game).count() == 5
    game.refresh_from_db()
    assert game.unrest == 4
