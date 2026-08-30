import pytest
from rorapp.actions.fight_land_battle import FightLandBattleAction
from rorapp.actions.halt_after_naval_victory import HaltAfterNavalVictoryAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Fleet, Game, Legion, Log, Senator, War


@pytest.mark.django_db
def test_naval_victory_with_legions_and_fleet_support_pauses_for_land_battle_decision(
    naval_campaign: Campaign,
):
    # Arrange
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    for i in range(1, 6):
        Legion.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.has_status_item(Senator.StatusItem.CONSIDERING_LAND_BATTLE)
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.RESOLUTION


@pytest.mark.django_db
def test_attacking_land_forces_after_naval_victory_eliminates_war(
    naval_campaign: Campaign,
):
    # Arrange
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    for i in range(1, 11):
        Legion.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18, 18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)
    faction = commander.faction
    assert faction is not None
    action = FightLandBattleAction()
    action.execute(game.id, faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    assert not War.objects.filter(game=game).exists()


@pytest.mark.django_db
def test_halting_after_naval_victory_leaves_war_intact(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    for i in range(1, 6):
        Legion.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)
    faction = commander.faction
    assert faction is not None
    action = HaltAfterNavalVictoryAction()
    action.execute(game.id, faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    war = War.objects.filter(game=game).first()
    assert war is not None
    assert war.land_strength > 0
    assert war.naval_strength == 0


@pytest.mark.django_db
def test_naval_victory_without_surviving_fleet_support_does_not_offer_land_battle(
    naval_campaign: Campaign,
):
    # Arrange — only 3 fleets against naval_strength=10; all fleets lost on a narrow victory
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 4):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    for i in range(1, 6):
        Legion.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert not commander.has_status_item(Senator.StatusItem.CONSIDERING_LAND_BATTLE)


@pytest.mark.django_db
def test_naval_victory_by_fleet_only_force_returns_fleets_to_the_reserve(
    naval_campaign: Campaign,
):
    # Arrange — a fleet-only force, so there are no legions left to fight on
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.location == "Rome"
    assert Fleet.objects.filter(game=game).count() == 10
    assert not Fleet.objects.filter(game=game, campaign__isnull=False).exists()
    assert not Campaign.objects.filter(game=game).exists()
    war = War.objects.get(game=game)
    assert war.naval_strength == 0


@pytest.mark.django_db
def test_naval_victory_by_fleet_only_force_logs_the_return(naval_campaign: Campaign):
    # Arrange
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 11):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    log_texts = list(Log.objects.filter(game=game).values_list("text", flat=True))
    assert (
        f"{commander.display_name} returned to Rome because no legions were "
        "present for the land battle. "
        "10 fleets (I–X) returned to the reserve forces." in log_texts
    )


@pytest.mark.django_db
def test_naval_victory_that_destroys_every_fleet_still_logs_the_return(
    naval_campaign: Campaign,
):
    # Arrange — only 3 fleets against naval_strength=10, so a narrow victory
    # destroys all of them and there is nothing to return to the reserve
    game = naval_campaign.game
    commander = naval_campaign.commander
    assert commander is not None
    for i in range(1, 4):
        Fleet.objects.create(game=game, number=i, campaign=naval_campaign)
    resolver = FakeRandomResolver()
    resolver.dice_rolls = [18]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert commander.location == "Rome"
    assert not Fleet.objects.filter(game=game).exists()
    assert not Campaign.objects.filter(game=game).exists()
    log_texts = list(Log.objects.filter(game=game).values_list("text", flat=True))
    assert (
        f"{commander.display_name} returned to Rome because no legions were "
        "present for the land battle." in log_texts
    )
