from typing import Callable

import pytest
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.helpers.force_strength import force_strength
from rorapp.helpers.resolve_combat import resolve_combat
from rorapp.models import Campaign, Game, Legion, Log, Senator, War


def _roll_for(army: Campaign, modified_result: int) -> int:
    """The 3d6 roll that gives this army the modified result wanted."""

    assert army.war is not None and army.commander is not None
    senate_strength = force_strength(
        sum(l.strength for l in army.legions.all()), army.commander.military
    )
    return modified_result - senate_strength + army.war.land_strength


def _fight(army: Campaign, resolver: FakeRandomResolver, modified_result: int):
    resolver.dice_rolls = [_roll_for(army, modified_result)]
    resolve_combat(army.game_id, army.id, resolver)


def _rebel(army: Campaign) -> Senator:
    return Senator.objects.get(game=army.game_id, family_name="Cornelius")


@pytest.mark.django_db
def test_losses_are_applied_to_both_armies(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6, 7, 8])

    # Act
    _fight(army, resolver, 12)

    # Assert
    assert Legion.objects.filter(campaign=army).count() == 3
    assert Legion.objects.filter(campaign__commander__rebel=True).count() == 3
    assert Log.objects.filter(
        game=army.game_id, text__contains="The rebels lost 1 legion (I)."
    ).exists()


@pytest.mark.django_db
def test_stalemate_leaves_the_revolt_standing_at_its_new_strength(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6, 7, 8])
    rebel = _rebel(army)

    # Act
    _fight(army, resolver, 12)

    # Assert
    revolt = War.objects.get(game=army.game_id, primary_rebel=rebel)
    assert revolt.status == War.Status.ACTIVE
    survivors = Legion.objects.filter(campaign__commander=rebel)
    assert survivors.count() == 3
    assert revolt.land_strength == force_strength(
        sum(l.strength for l in survivors), rebel.military
    )
    assert Game.objects.get(id=army.game_id).unrest == 3


@pytest.mark.django_db
def test_stalemate_hardens_a_legion_on_each_side(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6, 7, 8])
    rebel = _rebel(army)

    # Act
    _fight(army, resolver, 12)

    # Assert
    assert Legion.objects.get(game=army.game_id, number=2).allegiance == rebel
    assert Legion.objects.get(game=army.game_id, number=6).allegiance == army.commander


@pytest.mark.django_db
def test_senate_victory_kills_the_rebel_and_ends_the_revolt(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1, 2], senate_legions=[5, 6, 7, 8])
    rebel = _rebel(army)

    # Act
    _fight(army, resolver, 18)

    # Assert
    rebel.refresh_from_db()
    assert not rebel.rebel
    revolt = War.objects.get(game=army.game_id, name="Revolt")
    assert revolt.status == War.Status.DEFEATED
    assert Legion.objects.filter(game=army.game_id, number__in=[1, 2]).filter(
        campaign__isnull=True
    ).count() == 2
    assert Game.objects.get(id=army.game_id).unrest == 2


@pytest.mark.django_db
def test_senate_victor_keeps_his_command_until_the_revolution_phase(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1, 2], senate_legions=[5, 6, 7, 8])

    # Act
    _fight(army, resolver, 18)

    # Assert
    army.refresh_from_db()
    assert army.land_victory


@pytest.mark.django_db
def test_senate_victory_rewards_half_the_rebel_strength(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1, 2, 3], senate_legions=[5, 6, 7, 8])
    assert army.war is not None and army.commander is not None
    influence = army.commander.influence
    glory = (army.war.land_strength + 1) // 2

    # Act
    _fight(army, resolver, 18)

    # Assert
    army.commander.refresh_from_db()
    assert army.commander.influence == influence + glory


@pytest.mark.django_db
def test_senate_victory_sends_the_other_senate_armies_home(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(
        rebel_legions=[1, 2], senate_legions=[5, 6, 7, 8], other_senate_legions=[9]
    )
    other_commander = Senator.objects.get(game=army.game_id, family_name="Fabius")

    # Act
    _fight(army, resolver, 18)

    # Assert
    other_commander.refresh_from_db()
    assert other_commander.location == "Rome"
    assert Legion.objects.get(game=army.game_id, number=9).campaign is None


@pytest.mark.django_db
def test_senate_defeat_leaves_the_rebel_army_whole(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6])

    # Act
    _fight(army, resolver, 6)

    # Assert
    assert Legion.objects.filter(campaign__commander__rebel=True).count() == 4
    assert Game.objects.get(id=army.game_id).unrest == 3


@pytest.mark.django_db
def test_senate_defeat_sends_every_senate_army_to_the_reserve(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(
        rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6, 7], other_senate_legions=[9]
    )
    other_commander = Senator.objects.get(game=army.game_id, family_name="Fabius")

    # Act
    _fight(army, resolver, 6)

    # Assert
    other_commander.refresh_from_db()
    assert other_commander.location == "Rome"
    assert Legion.objects.filter(
        game=army.game_id, number__in=[5, 6, 7, 9], campaign__isnull=False
    ).count() == 0


@pytest.mark.django_db
def test_senate_defeat_hardens_a_rebel_legion(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6])

    # Act
    _fight(army, resolver, 6)

    # Assert
    assert Legion.objects.get(game=army.game_id, number=1).allegiance == _rebel(army)


@pytest.mark.django_db
def test_a_mortality_chit_can_kill_the_rebel(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1, 2, 3, 4], senate_legions=[5, 6, 7, 8])
    rebel = _rebel(army)
    resolver.mortality_chits = [[rebel.code]]

    # Act
    _fight(army, resolver, 12)

    # Assert
    rebel.refresh_from_db()
    assert not rebel.rebel
    assert War.objects.get(game=army.game_id, name="Revolt").status == (
        War.Status.DEFEATED
    )
    assert army.commander is not None
    army.commander.refresh_from_db()
    assert army.commander.location == "Rome"


@pytest.mark.django_db
def test_rebel_who_loses_his_army_is_killed_and_the_revolt_fails(
    revolt_battle: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    army = revolt_battle(rebel_legions=[1], senate_legions=[5, 6, 7, 8])
    rebel = _rebel(army)

    # Act
    _fight(army, resolver, 12)

    # Assert
    rebel.refresh_from_db()
    assert not rebel.rebel
    assert rebel.location == "Rome"
    assert War.objects.get(game=army.game_id, name="Revolt").status == (
        War.Status.DEFEATED
    )
    assert Log.objects.filter(
        game=army.game_id, text="Cornelius lost the last of his army."
    ).exists()
    assert Log.objects.filter(
        game=army.game_id, text="The revolt ended with the death of Cornelius."
    ).exists()
    assert Log.objects.filter(
        game=army.game_id, text__contains="bringing an end to the Revolt."
    ).exists()
