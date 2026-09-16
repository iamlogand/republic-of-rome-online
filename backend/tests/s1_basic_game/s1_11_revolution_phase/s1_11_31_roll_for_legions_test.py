from typing import Callable

import pytest
from rorapp.actions.declare_revolt import DeclareRevoltAction
from rorapp.actions.lay_down_command import LayDownCommandAction
from rorapp.actions.roll_for_legions import RollForLegionsAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Campaign, Game, Legion, Log, Senator

pytestmark = pytest.mark.usefixtures("civil_war_flag")


def _roll(campaign: Campaign, resolver: FakeRandomResolver, bribed=()):
    game = campaign.game
    execute_effects_and_manage_actions(game.id, resolver)
    commander = campaign.commander
    assert commander is not None and commander.faction_id is not None
    return RollForLegionsAction().execute(
        game.id,
        commander.faction_id,
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
    assert Log.objects.filter(
        game=campaign.game, text="Cornelius spent 1T on the loyalty of Legion I."
    ).exists()


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
    execute_effects_and_manage_actions(campaign.game.id, resolver)
    commander = campaign.commander
    assert commander is not None and commander.faction_id is not None

    # Act
    faction = RollForLegionsAction().is_allowed(
        GameStateSnapshot(campaign.game.id), commander.faction_id
    )

    # Assert
    assert faction is None


@pytest.mark.django_db
def test_a_victor_who_may_not_declare_may_not_roll(
    add_land_victor: Callable[..., Campaign], resolver: FakeRandomResolver
):
    # Arrange
    stronger = add_land_victor("Cornelius", [1, 2, 3, 4, 5])
    weaker = add_land_victor("Manlius", [6, 7, 8, 9, 10])
    game = stronger.game
    execute_effects_and_manage_actions(game.id, resolver)
    assert stronger.commander is not None and stronger.commander.faction_id
    DeclareRevoltAction().execute(
        game.id, stronger.commander.faction_id, {}, resolver
    )
    execute_effects_and_manage_actions(game.id, resolver)
    assert weaker.commander is not None and weaker.commander.faction_id

    # Act
    faction = RollForLegionsAction().is_allowed(
        GameStateSnapshot(game.id), weaker.commander.faction_id
    )

    # Assert
    assert faction is None


@pytest.mark.django_db
def test_a_commander_who_lays_down_command_may_roll_again_next_turn(
    land_victor: Campaign, resolver: FakeRandomResolver
):
    # Arrange
    game = land_victor.game
    commander = land_victor.commander
    assert commander is not None and commander.faction_id is not None
    resolver.dice_rolls = [5, 5, 5, 5, 5]
    _roll(land_victor, resolver)

    # Act
    LayDownCommandAction().execute(game.id, commander.faction_id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.phase != Game.Phase.REVOLUTION
    commander.refresh_from_db()
    assert not commander.has_status_item(Senator.StatusItem.ROLLED_FOR_LEGIONS)


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


@pytest.mark.django_db
def test_rolling_is_not_offered_with_the_flag_off(
    land_victor: Campaign, settings
):
    # Arrange
    game = land_victor.game
    game.sub_phase = Game.SubPhase.REVOLT_DECLARATION
    game.save()
    commander = land_victor.commander
    assert commander is not None and commander.faction is not None
    commander.faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    commander.faction.save()
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, "civil_war": False}

    # Act
    faction = RollForLegionsAction().is_allowed(
        GameStateSnapshot(game.id), commander.faction.id
    )

    # Assert
    assert faction is None
