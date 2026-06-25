import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game


def _setup_initiative_roll(game: Game, faction: Faction) -> None:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
    game.deck = ["senator:18"]
    game.save()
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_allied_enthusiasm(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.has_effect(GameEffect.ALLIED_ENTHUSIASM)
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 1


@pytest.mark.django_db
def test_rolling_7_does_not_draw_a_card(basic_game: Game, resolver: FakeRandomResolver):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert len(game.deck) == 1


@pytest.mark.django_db
def test_drawing_allied_enthusiasm_twice_escalates_to_extreme(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 2


@pytest.mark.django_db
def test_rolling_unimplemented_event_draws_a_card_instead(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [
        7,
        11,
    ]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert len(game.deck) == 0


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_drought(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 9]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.DROUGHT) == 1


@pytest.mark.django_db
def test_drawing_drought_beyond_severe_still_increases_famine(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.DROUGHT)
    game.add_effect(GameEffect.DROUGHT)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 9]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.DROUGHT) == 3


@pytest.mark.django_db
def test_rolling_7_on_initiative_triggers_manpower_shortage(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 12]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.MANPOWER_SHORTAGE) == 1


@pytest.mark.django_db
def test_drawing_manpower_shortage_twice_stacks(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.MANPOWER_SHORTAGE)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 12]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.MANPOWER_SHORTAGE) == 2


@pytest.mark.django_db
def test_drawing_allied_enthusiasm_at_max_has_no_effect(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.add_effect(GameEffect.ALLIED_ENTHUSIASM)
    game.save()
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction)
    resolver.dice_rolls = [7, 13]

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.count_effect(GameEffect.ALLIED_ENTHUSIASM) == 2
