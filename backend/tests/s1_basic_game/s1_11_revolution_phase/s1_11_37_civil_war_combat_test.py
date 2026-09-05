from typing import Callable

import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Legion, Log, Senator, War


@pytest.mark.django_db
def test_the_rebel_army_defends_with_its_maintained_strength(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(rebel_legions=[1, 2, 3], senate_legions=[4, 5, 6, 7])
    game = senate_campaign.game
    war = War.objects.get(game=game, primary_rebel__isnull=False)
    resolver.dice_rolls = [10]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert war.land_strength == 6
    assert Log.objects.filter(
        game=game, text__contains="Civil War Stalemate"
    ).exists()


@pytest.mark.django_db
def test_losses_are_applied_to_both_armies(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6, 7, 8]
    )
    game = senate_campaign.game
    rebel_campaign = Campaign.objects.get(game=game, war__isnull=True)
    resolver.dice_rolls = [13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert Legion.objects.filter(game=game, campaign=senate_campaign).count() == 3
    assert Legion.objects.filter(game=game, campaign=rebel_campaign).count() == 3


@pytest.mark.django_db
def test_the_rebel_army_takes_no_losses_in_a_senate_defeat(
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
    assert Legion.objects.filter(game=game, campaign=rebel_campaign).count() == 4


@pytest.mark.django_db
def test_a_rebel_master_of_horse_adds_his_military_rating(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2, 3, 4, 5],
        senate_legions=[6, 7],
        rebel_master_of_horse_name="Fabius",
    )
    game = senate_campaign.game
    war = War.objects.get(game=game, primary_rebel__isnull=False)
    from rorapp.helpers.civil_war import refresh_civil_war_strength

    refresh_civil_war_strength(game.id)
    war.refresh_from_db()

    # Act
    strength = war.land_strength

    # Assert
    assert strength == 10


@pytest.mark.django_db
def test_mortality_chits_can_kill_the_rebel(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(rebel_legions=[1, 2, 3], senate_legions=[4, 5, 6, 7])
    game = senate_campaign.game
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    resolver.dice_rolls = [10]
    resolver.mortality_chits = [[rebel.code]]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    rebel.refresh_from_db()
    assert rebel.alive == False
    assert War.objects.filter(game=game, primary_rebel__isnull=False).exists() == False
