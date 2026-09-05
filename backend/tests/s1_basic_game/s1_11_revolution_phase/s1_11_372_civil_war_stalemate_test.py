from typing import Callable

import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Game, Legion, Senator, War


@pytest.mark.django_db
def test_the_civil_war_survives_a_stalemate(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6, 7, 8]
    )
    game = senate_campaign.game
    resolver.dice_rolls = [13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert War.objects.filter(game=game, primary_rebel__isnull=False).exists()
    game.refresh_from_db()
    assert game.unrest == 3


@pytest.mark.django_db
def test_one_legion_on_each_side_becomes_a_veteran(
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
    assert (
        Legion.objects.filter(
            game=game, campaign=senate_campaign, veteran=True
        ).count()
        == 1
    )
    assert (
        Legion.objects.filter(game=game, campaign=rebel_campaign, veteran=True).count()
        == 1
    )


@pytest.mark.django_db
def test_the_revolt_fails_when_the_rebel_loses_his_last_legion(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2],
        senate_legions=[3, 4, 5],
        rebel_master_of_horse_name="Fabius",
    )
    game = senate_campaign.game
    resolver.dice_rolls = [9]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    rebel = Senator.objects.get(game=game, family_name="Cornelius")
    secondary = Senator.objects.get(game=game, family_name="Fabius")
    assert rebel.alive == True
    assert rebel.rebel == True
    assert secondary.alive == False
    assert War.objects.filter(game=game, primary_rebel__isnull=False).exists() == False


@pytest.mark.django_db
def test_the_senate_commander_returns_to_rome_when_the_revolt_fails(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(rebel_legions=[1, 2], senate_legions=[3, 4, 5])
    game = senate_campaign.game
    resolver.dice_rolls = [9]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander = Senator.objects.get(game=game, family_name="Manlius")
    assert commander.location == "Rome"
    assert not commander.has_title(Senator.Title.PROCONSUL)
    assert Campaign.objects.filter(game=game).exists() == False


@pytest.mark.django_db
def test_the_senate_may_attack_again_next_turn(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(
        rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6, 7, 8]
    )
    game = senate_campaign.game
    resolver.dice_rolls = [13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase == Game.Phase.REVOLUTION
    war = War.objects.get(game=game, primary_rebel__isnull=False)
    assert war.status == War.Status.ACTIVE
