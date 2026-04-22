import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.effects.roll_assassination_dice import RollAssassinationDiceEffect
from rorapp.models import Game, Senator


def _setup_assassination_roll(
    game: Game,
    assassin: Senator,
    target: Senator,
    interrupted_sub_phase: str = Game.SubPhase.OTHER_BUSINESS,
    modifier: int = 0,
):
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
    game.assassination_roll_result = 0
    game.assassination_roll_modifier = modifier
    game.bodyguard_rerolls_remaining = 0
    game.interrupted_sub_phase = interrupted_sub_phase
    game.save()
    assassin.add_status_item(Senator.StatusItem.ASSASSIN)
    assassin.save()
    target.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
    target.save()


@pytest.mark.parametrize(
    "roll,should_catch,target_dies",
    [
        (1, True, False),
        (2, True, False),
        (3, False, False),
        (4, False, False),
        (5, False, True),
        (6, False, True),
    ],
)
@pytest.mark.django_db
def test_assassination_roll_outcome(
    senate_game: Game, resolver: FakeRandomResolver, roll, should_catch, target_dies
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_assassination_roll(game, cornelius, claudius)
    resolver.dice_rolls = [roll]
    resolver.mortality_chits = []

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    cornelius.refresh_from_db()
    claudius.refresh_from_db()
    assert claudius.alive != target_dies
    assert cornelius.alive == (not should_catch)


@pytest.mark.django_db
def test_assassination_modifier_raises_roll_result(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_assassination_roll(game, cornelius, claudius, modifier=1)
    resolver.dice_rolls = [4]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    claudius.refresh_from_db()
    assert not claudius.alive


@pytest.mark.django_db
def test_awaiting_decision_set_when_target_faction_has_cards_and_result_above_2(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.faction.cards = ["secret bodyguard"]
    claudius.faction.save()
    _setup_assassination_roll(game, cornelius, claudius)
    resolver.dice_rolls = [5]

    # Act
    RollAssassinationDiceEffect().execute(game.id, resolver)

    # Assert
    claudius.faction.refresh_from_db()
    assert claudius.faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_awaiting_decision_set_even_when_faction_holds_non_bodyguard_card(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.faction.cards = ["assassin"]
    claudius.faction.save()
    _setup_assassination_roll(game, cornelius, claudius)
    resolver.dice_rolls = [5]

    # Act
    RollAssassinationDiceEffect().execute(game.id, resolver)

    # Assert
    claudius.faction.refresh_from_db()
    assert claudius.faction.has_status_item(FactionStatusItem.AWAITING_DECISION)


@pytest.mark.django_db
def test_awaiting_decision_not_set_when_roll_is_1_or_2(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    claudius.faction.cards = ["secret bodyguard"]
    claudius.faction.save()
    _setup_assassination_roll(game, cornelius, claudius)
    resolver.dice_rolls = [2]

    # Act
    RollAssassinationDiceEffect().execute(game.id, resolver)

    # Assert
    claudius.faction.refresh_from_db()
    cornelius.refresh_from_db()
    assert not claudius.faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
    assert cornelius.has_status_item(Senator.StatusItem.CAUGHT)


@pytest.mark.django_db
def test_game_returns_to_interrupted_sub_phase_after_no_effect_roll(
    senate_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = senate_game
    cornelius = Senator.objects.get(game=game, family_name="Cornelius")
    claudius = Senator.objects.get(game=game, family_name="Claudius")
    _setup_assassination_roll(
        game, cornelius, claudius, interrupted_sub_phase=Game.SubPhase.OTHER_BUSINESS
    )
    resolver.dice_rolls = [4]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.sub_phase == Game.SubPhase.OTHER_BUSINESS
    assert game.interrupted_sub_phase == ""
    assert game.assassination_roll_result == 0
