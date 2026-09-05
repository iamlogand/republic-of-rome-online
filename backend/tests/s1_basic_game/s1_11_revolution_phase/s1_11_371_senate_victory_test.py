from typing import Callable

import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Legion, Senator, War


def _win(senate_campaign: Campaign, resolver: FakeRandomResolver) -> None:
    resolver.dice_rolls = [18]
    execute_effects_and_manage_actions(senate_campaign.game.id, resolver)


@pytest.mark.django_db
def test_every_rebel_senator_is_killed(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2],
        senate_legions=[3, 4, 5, 6, 7, 8],
        rebel_master_of_horse_name="Fabius",
    )
    game = senate_campaign.game

    # Act
    _win(senate_campaign, resolver)

    # Assert
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    secondary = Senator.objects.get(game=game, family_name="Fabius")
    assert rebel.alive == False
    assert secondary.alive == False
    assert War.objects.filter(game=game, primary_rebel__isnull=False).exists() == False


@pytest.mark.django_db
def test_surviving_rebel_legions_return_to_the_reserve(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6, 7, 8, 9, 10]
    )
    game = senate_campaign.game

    # Act
    _win(senate_campaign, resolver)

    # Assert
    assert Legion.objects.filter(game=game, campaign__isnull=True).count() > 0
    assert Campaign.objects.filter(game=game, war__isnull=True).count() == 1


@pytest.mark.django_db
def test_unrest_falls_by_one(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2], senate_legions=[3, 4, 5, 6, 7, 8]
    )
    game = senate_campaign.game

    # Act
    _win(senate_campaign, resolver)

    # Assert
    game.refresh_from_db()
    assert game.unrest == 2


@pytest.mark.django_db
def test_the_senate_commander_gains_half_the_rebel_strength(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2, 3], senate_legions=[4, 5, 6, 7, 8, 9, 10]
    )
    game = senate_campaign.game
    commander = Senator.objects.get(game=game, family_name="Manlius")
    influence_before = commander.influence

    # Act
    _win(senate_campaign, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.influence == influence_before + 3
    assert commander.popularity == 3


@pytest.mark.django_db
def test_the_senate_commander_keeps_his_army_and_may_revolt(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2], senate_legions=[3, 4, 5, 6, 7, 8]
    )
    game = senate_campaign.game

    # Act
    _win(senate_campaign, resolver)

    # Assert
    senate_campaign.refresh_from_db()
    assert senate_campaign.land_victory == True
    assert senate_campaign.war is None
    commander = Senator.objects.get(game=game, family_name="Manlius")
    assert commander.location == "Italia"
