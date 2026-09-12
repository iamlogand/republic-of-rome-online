from typing import Callable

import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.civil_war import get_civil_war
from rorapp.helpers.resolve_civil_war import resolve_civil_war
from rorapp.models import Campaign, Legion, Senator


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
    assert get_civil_war(game.id) is None


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
    assert Campaign.objects.filter(game=game).count() == 1


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
    commander = Senator.objects.get(game=game, family_name="Manlius")
    assert commander.location == "Italia"


@pytest.mark.django_db
def test_other_senate_army_returns_to_rome_without_its_title(
    civil_war: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    senate_campaign = civil_war(rebel_legions=[1, 2], senate_legions=list(range(3, 13)))
    war = senate_campaign.war
    assert war is not None
    proconsul = Senator.objects.get(game=war.game, family_name="Fulvius")
    proconsul.add_title(Senator.Title.PROCONSUL)
    proconsul.location = "Italia"
    proconsul.save()
    Campaign.objects.create(
        game=war.game, war=war, commander=proconsul, recently_deployed=False
    )
    resolver.dice_rolls = [18]

    # Act
    resolve_civil_war(senate_campaign.game_id, senate_campaign.id, resolver)

    # Assert
    proconsul.refresh_from_db()
    assert proconsul.location == "Rome"
    assert not proconsul.has_title(Senator.Title.PROCONSUL)
