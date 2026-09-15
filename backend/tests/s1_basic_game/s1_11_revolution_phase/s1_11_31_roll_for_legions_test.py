from typing import Callable

import pytest
from rorapp.actions.roll_for_legions import RollForLegionsAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Legion, Log, Senator


def _roll(campaign: Campaign, resolver: FakeRandomResolver, bribed=()):
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    commander = campaign.commander
    assert commander is not None and commander.faction is not None
    return RollForLegionsAction().execute(
        game.id,
        commander.faction.id,
        {"Legions to bribe": [str(l.id) for l in bribed]},
        resolver,
    )


@pytest.mark.django_db
def test_legions_rolling_five_or_more_follow_the_commander(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2, 3])
    resolver.dice_rolls = [5, 6, 5]

    # Act
    _roll(campaign, resolver)

    # Assert
    assert Legion.objects.filter(game=campaign.game, campaign=campaign).count() == 3


@pytest.mark.django_db
def test_legions_rolling_below_five_return_to_the_reserve(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2, 3])
    resolver.dice_rolls = [4, 5, 1]

    # Act
    _roll(campaign, resolver)

    # Assert
    remaining = Legion.objects.filter(game=campaign.game, campaign=campaign)
    assert [l.number for l in remaining] == [2]
    assert Legion.objects.filter(game=campaign.game, campaign__isnull=True).count() == 2


@pytest.mark.django_db
def test_a_bribed_legion_follows_on_a_four(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])
    commander = campaign.commander
    assert commander is not None
    commander.talents = 1
    commander.save()
    bribed = Legion.objects.filter(game=campaign.game, number=1)
    resolver.dice_rolls = [4, 4]

    # Act
    _roll(campaign, resolver, bribed=bribed)

    # Assert
    remaining = Legion.objects.filter(game=campaign.game, campaign=campaign)
    assert [l.number for l in remaining] == [1]
    commander.refresh_from_db()
    assert commander.talents == 0


@pytest.mark.django_db
def test_veteran_owing_allegiance_to_the_commander_does_not_roll(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])
    veteran = Legion.objects.get(game=campaign.game, number=1)
    veteran.veteran = True
    veteran.allegiance = campaign.commander
    veteran.save()
    resolver.dice_rolls = [1]

    # Act
    _roll(campaign, resolver)

    # Assert
    remaining = Legion.objects.filter(game=campaign.game, campaign=campaign)
    assert [l.number for l in remaining] == [1]


@pytest.mark.django_db
def test_veteran_owing_allegiance_elsewhere_must_roll(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1])
    veteran = Legion.objects.get(game=campaign.game, number=1)
    veteran.veteran = True
    veteran.allegiance = Senator.objects.get(game=campaign.game, family_name="Manlius")
    veteran.save()
    resolver.dice_rolls = [1]

    # Act
    _roll(campaign, resolver)

    # Assert
    assert Legion.objects.filter(game=campaign.game, campaign=campaign).count() == 0


@pytest.mark.django_db
def test_bribes_are_limited_to_available_talents(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])
    bribed = Legion.objects.filter(game=campaign.game)

    # Act
    result = _roll(campaign, resolver, bribed=bribed)

    # Assert
    assert result.success == False
    assert Legion.objects.filter(game=campaign.game, campaign=campaign).count() == 2


@pytest.mark.django_db
def test_master_of_horse_pays_when_the_commander_runs_out(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2], master_of_horse_name="Fabius")
    commander = campaign.commander
    master_of_horse = campaign.master_of_horse
    assert commander is not None and master_of_horse is not None
    commander.talents = 1
    commander.save()
    master_of_horse.talents = 3
    master_of_horse.save()
    resolver.dice_rolls = [4, 4]

    # Act
    _roll(campaign, resolver, bribed=Legion.objects.filter(game=campaign.game))

    # Assert
    commander.refresh_from_db()
    master_of_horse.refresh_from_db()
    assert commander.talents == 0
    assert master_of_horse.talents == 2
    assert Legion.objects.filter(game=campaign.game, campaign=campaign).count() == 2


@pytest.mark.django_db
def test_legions_may_only_be_rolled_for_once(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2])
    resolver.dice_rolls = [5, 5]
    _roll(campaign, resolver)

    # Act
    result = _roll(campaign, resolver)

    # Assert
    assert result.success == False


@pytest.mark.django_db
def test_refusing_legions_are_logged(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    campaign = add_land_victor("Cornelius", [1, 2, 3])
    resolver.dice_rolls = [1, 1, 5]

    # Act
    _roll(campaign, resolver)

    # Assert
    assert Log.objects.filter(
        game=campaign.game,
        text="2 legions (I and II) refused to follow Cornelius and returned to "
        "the reserve forces.",
    ).exists()
