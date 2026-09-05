from typing import Callable

import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Senator


@pytest.mark.django_db
def test_the_rebel_wins_when_the_senate_does_not_attack(
    rebel_army: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    game = rebel_army().game

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.finished_on is not None


@pytest.mark.django_db
def test_the_rebel_wins_by_beating_the_senate_in_battle(
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
    assert game.finished_on is not None
    assert game.rebel_winning_condition == 1


@pytest.mark.django_db
def test_the_rebel_does_not_win_if_he_dies_in_the_battle(
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
    game.refresh_from_db()
    assert game.rebel_winning_condition == 0
    assert game.finished_on is None
