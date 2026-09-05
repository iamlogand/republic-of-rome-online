from typing import Callable

import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Legion, Senator, War


@pytest.mark.django_db
def test_the_senate_commander_and_his_master_of_horse_are_killed(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2, 3, 4],
        senate_legions=[5, 6],
        master_of_horse_name="Fulvius",
    )
    game = senate_campaign.game
    resolver.dice_rolls = [6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander = Senator.objects.get(game=game, family_name="Manlius")
    master_of_horse = Senator.objects.get(game=game, family_name="Fulvius")
    assert commander.alive == False
    assert master_of_horse.alive == False


@pytest.mark.django_db
def test_surviving_senate_armies_return_to_the_reserve(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(rebel_legions=[1, 2, 3, 4, 5], senate_legions=[6, 7])
    game = senate_campaign.game
    resolver.dice_rolls = [12]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Campaign.objects.filter(game=game, war__isnull=False).exists() == False
    assert (
        Legion.objects.filter(game=game, campaign__isnull=True, number__in=[6, 7])
        .count()
        > 0
    )


@pytest.mark.django_db
def test_unrest_is_unchanged(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6])
    game = senate_campaign.game
    resolver.dice_rolls = [6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 3


@pytest.mark.django_db
def test_a_rebel_legion_becomes_a_veteran(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6])
    game = senate_campaign.game
    rebel_campaign = Campaign.objects.get(game=game, war__isnull=True)
    resolver.dice_rolls = [6]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert (
        Legion.objects.filter(game=game, campaign=rebel_campaign, veteran=True).count()
        == 1
    )


@pytest.mark.django_db
def test_the_revolt_fails_if_the_rebel_dies_in_the_battle(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6])
    game = senate_campaign.game
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    resolver.dice_rolls = [6]
    resolver.mortality_chits = [[rebel.code]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    rebel.refresh_from_db()
    assert rebel.alive == False
    assert War.objects.filter(game=game, primary_rebel__isnull=False).exists() == False
