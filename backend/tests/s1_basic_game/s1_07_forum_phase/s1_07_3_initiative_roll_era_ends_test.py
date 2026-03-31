import pytest
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.models import Faction, Game, Log


def _setup_initiative_roll(game: Game, faction: Faction, deck: list) -> None:
    game.phase = Game.Phase.FORUM
    game.sub_phase = Game.SubPhase.INITIATIVE_ROLL
    game.deck = deck
    game.save()
    faction.add_status_item(FactionStatusItem.CURRENT_INITIATIVE)
    faction.save()


@pytest.mark.django_db
def test_drawing_era_ends_sets_era_ends_flag(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction, ["era ends"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    game.refresh_from_db()
    assert game.era_ends is True


@pytest.mark.django_db
def test_drawing_era_ends_is_not_added_to_faction_hand(
    basic_game: Game, resolver: FakeRandomResolver
):
    # Arrange
    game = basic_game
    faction: Faction = game.factions.get(position=1)
    _setup_initiative_roll(game, faction, ["era ends"])

    # Act
    execute_effects_and_manage_actions(game.id, resolver)

    # Assert
    faction.refresh_from_db()
    assert "era ends" not in faction.cards
