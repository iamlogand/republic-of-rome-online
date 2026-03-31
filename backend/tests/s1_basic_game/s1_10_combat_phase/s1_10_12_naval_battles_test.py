import pytest
from rorapp.actions.attack_land_forces import AttackLandForcesAction
from rorapp.actions.halt_after_naval_victory import HaltAfterNavalVictoryAction
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Campaign, Fleet, Game, Legion, Senator, War


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
    resolver.casualty_order = []
    resolver.mortality_chits = []

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
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)
    faction = commander.faction
    assert faction is not None
    action = AttackLandForcesAction()
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
    resolver.casualty_order = []
    resolver.mortality_chits = []

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
    resolver.casualty_order = []
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    commander.refresh_from_db()
    assert not commander.has_status_item(Senator.StatusItem.CONSIDERING_LAND_BATTLE)
