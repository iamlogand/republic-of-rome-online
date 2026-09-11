import pytest

from rorapp.actions.done import DoneAction
from rorapp.actions.done_not import DoneNotAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game


READINESS_PHASES = [
    (Game.Phase.REVENUE, Game.SubPhase.REDISTRIBUTION),
    (Game.Phase.REVOLUTION, Game.SubPhase.CARD_TRADING),
]


@pytest.mark.django_db
@pytest.mark.parametrize(("phase", "sub_phase"), READINESS_PHASES)
def test_done_action_is_displayed_as_ready(
    basic_game: Game, phase: str, sub_phase: str
):
    # Arrange
    game = basic_game
    game.phase = phase
    game.sub_phase = sub_phase
    game.save()
    faction = game.factions.first()
    assert faction is not None

    # Act
    [action] = DoneAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert action.base_name == DoneAction.NAME
    assert action.variant_name == "Ready"
    assert action.name == "Ready"


@pytest.mark.django_db
@pytest.mark.parametrize(("phase", "sub_phase"), READINESS_PHASES)
def test_not_done_action_is_displayed_as_not_ready(
    basic_game: Game, phase: str, sub_phase: str
):
    # Arrange
    game = basic_game
    game.phase = phase
    game.sub_phase = sub_phase
    game.save()
    faction = game.factions.first()
    assert faction is not None
    faction.add_status_item(FactionStatusItem.DONE)
    faction.save()

    # Act
    [action] = DoneNotAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert action.base_name == DoneNotAction.NAME
    assert action.variant_name == "Not ready"
    assert action.name == "Not ready"


@pytest.mark.django_db
@pytest.mark.parametrize("phase", [Game.Phase.INITIAL, Game.Phase.REVOLUTION])
def test_done_action_keeps_its_name_when_playing_cards(
    basic_game: Game, phase: str
):
    # Arrange
    game = basic_game
    game.phase = phase
    game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
    game.save()
    faction = game.factions.first()
    assert faction is not None
    faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
    faction.save()

    # Act
    [action] = DoneAction().get_schema(GameStateSnapshot(game.id), faction.id)

    # Assert
    assert action.base_name == DoneAction.NAME
    assert action.variant_name is None
    assert action.name == "Done"
