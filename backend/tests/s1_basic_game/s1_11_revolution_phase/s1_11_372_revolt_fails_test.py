from typing import Callable

import pytest
from rorapp.actions.declare_revolt import DeclareRevoltAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.helpers.kill_senator import kill_senator
from rorapp.models import Campaign, Legion, Log, Senator, War

pytestmark = pytest.mark.usefixtures("civil_war_flag")


def _declare(campaign: Campaign, resolver: FakeRandomResolver) -> War:
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    commander = campaign.commander
    assert commander is not None and commander.faction_id is not None
    DeclareRevoltAction().execute(game.id, commander.faction_id, {}, resolver)
    return War.objects.get(game=game, primary_rebel=commander)


@pytest.mark.django_db
def test_revolt_fails_when_the_primary_rebel_dies(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    revolt = _declare(land_victor, resolver)
    rebel = land_victor.commander
    assert rebel is not None

    # Act
    kill_senator(rebel)

    # Assert
    revolt.refresh_from_db()
    assert revolt.status == War.Status.DEFEATED
    assert not Campaign.objects.filter(war=revolt).exists()
    assert Legion.objects.filter(game=revolt.game, campaign__isnull=True).count() == 5
    assert Log.objects.filter(game=revolt.game, text="The revolt ended with the death of Cornelius.").exists()


@pytest.mark.django_db
def test_senate_army_facing_the_rebel_returns_to_rome(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    revolt = _declare(land_victor, resolver)
    game = revolt.game
    senate_commander = Senator.objects.get(game=game, family_name="Manlius")
    senate_commander.location = "Italia"
    senate_commander.add_title(Senator.Title.PROCONSUL)
    senate_commander.save()
    senate_army = Campaign.objects.create(
        game=game, war=revolt, commander=senate_commander
    )
    Legion.objects.create(game=game, number=6, campaign=senate_army)
    rebel = land_victor.commander
    assert rebel is not None

    # Act
    kill_senator(rebel)

    # Assert
    senate_commander.refresh_from_db()
    assert senate_commander.location == "Rome"
    assert not senate_commander.has_title(Senator.Title.PROCONSUL)
    assert Legion.objects.get(game=game, number=6).campaign is None


@pytest.mark.django_db
def test_heir_of_a_rebel_faction_leader_is_not_a_rebel(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    _declare(land_victor, resolver)
    rebel = land_victor.commander
    assert rebel is not None
    rebel.refresh_from_db()
    rebel.add_title(Senator.Title.FACTION_LEADER)
    rebel.save()

    # Act
    kill_senator(rebel)

    # Assert
    rebel.refresh_from_db()
    assert rebel.alive
    assert rebel.rebel == False


@pytest.mark.django_db
def test_revolt_fails_when_a_rebel_without_a_family_dies(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    revolt = _declare(land_victor, resolver)
    rebel = land_victor.commander
    assert rebel is not None
    rebel.refresh_from_db()
    rebel.family = False
    rebel.save()

    # Act
    kill_senator(rebel)

    # Assert
    revolt.refresh_from_db()
    assert revolt.status == War.Status.DEFEATED
    assert revolt.primary_rebel is None
