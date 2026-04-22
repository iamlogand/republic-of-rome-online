import pytest
from rorapp.actions.play_secret_bodyguard import PlaySecretBodyguardAction
from rorapp.actions.skip import SkipAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Game, Senator


def _setup_bodyguard_decision(
    game: Game,
    assassin: Senator,
    target: Senator,
    roll_result: int,
    modifier: int = 0,
):
    """Set game in ASSASSINATION_RESOLUTION awaiting target faction's bodyguard decision."""
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = roll_result
    game.assassination_roll_modifier = modifier
    game.bodyguard_rerolls_remaining = 0
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    assassin.add_status_item(Senator.StatusItem.ASSASSIN)
    assassin.save()
    target.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    target.save()
    target.faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    target.faction.save()


@pytest.mark.django_db
def test_bodyguard_subtracts_from_roll_result(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    target_faction = claudius.faction
    target_faction.cards = ["secret bodyguard", "secret bodyguard"]
    target_faction.save()
    _setup_bodyguard_decision(game, cornelius, claudius, roll_result=6)

    # Act
    PlaySecretBodyguardAction().execute(
        game.id, target_faction.id, {"Secret bodyguards to play": "2"}, resolver
    )

    # Assert
    game.refresh_from_db()
    assert game.assassination_roll_result == 4


@pytest.mark.django_db
def test_bodyguard_subtraction_to_le_2_catches_assassin_immediately(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    target_faction = claudius.faction
    target_faction.cards = ["secret bodyguard", "secret bodyguard", "secret bodyguard"]
    target_faction.save()
    _setup_bodyguard_decision(game, cornelius, claudius, roll_result=5)

    # Act
    PlaySecretBodyguardAction().execute(
        game.id, target_faction.id, {"Secret bodyguards to play": "3"}, resolver
    )

    # Assert
    game.refresh_from_db()
    assert game.assassination_roll_result == 2
    assert game.bodyguard_rerolls_remaining == 0
    cornelius.refresh_from_db()
    assert cornelius.has_status_item(Senator.StatusItem.CAUGHT)


@pytest.mark.django_db
def test_bodyguard_schedules_catch_rerolls_when_result_still_above_2(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    target_faction = claudius.faction
    target_faction.cards = ["secret bodyguard", "secret bodyguard"]
    target_faction.save()
    _setup_bodyguard_decision(game, cornelius, claudius, roll_result=6)

    # Act
    PlaySecretBodyguardAction().execute(
        game.id, target_faction.id, {"Secret bodyguards to play": "2"}, resolver
    )

    # Assert
    game.refresh_from_db()
    assert game.bodyguard_rerolls_remaining == 2


@pytest.mark.django_db
def test_catch_reroll_le_2_catches_assassin(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = 5
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 1
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    cornelius.add_status_item(Senator.StatusItem.ASSASSIN)
    cornelius.save()
    claudius.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    claudius.save()
    resolver.dice_rolls = [1]
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    claudius.refresh_from_db()
    assert not cornelius.alive
    assert not claudius.alive


@pytest.mark.django_db
def test_catch_reroll_above_2_does_not_catch_assassin(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = 5
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 1
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    cornelius.add_status_item(Senator.StatusItem.ASSASSIN)
    cornelius.save()
    claudius.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    claudius.save()
    resolver.dice_rolls = [4]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    claudius.refresh_from_db()
    assert cornelius.alive
    assert not claudius.alive


@pytest.mark.django_db
def test_target_killed_and_assassin_caught_by_subsequent_reroll(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = 5  # after bodyguard subtraction: still a kill
    game.assassination_roll_modifier = 0
    game.bodyguard_rerolls_remaining = 1  # 1 catch reroll pending
    game.interrupted_sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    cornelius.add_status_item(Senator.StatusItem.ASSASSIN)
    cornelius.save()
    claudius.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    claudius.save()
    resolver.dice_rolls = [2]  # catch reroll = 2 → Caught
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    claudius.refresh_from_db()
    assert not cornelius.alive
    assert not claudius.alive


@pytest.mark.django_db
def test_skip_action_removes_awaiting_decision(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    target_faction = claudius.faction
    _setup_bodyguard_decision(game, cornelius, claudius, roll_result=5)
    resolver.mortality_chits = []

    # Act
    SkipAction().execute(game.id, target_faction.id, {}, resolver)
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    target_faction.refresh_from_db()
    assert not target_faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    claudius.refresh_from_db()
    assert not claudius.alive
