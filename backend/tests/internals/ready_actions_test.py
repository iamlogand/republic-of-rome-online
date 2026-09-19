import pytest

from rorapp.actions.done import DoneAction
from rorapp.actions.meta.action_manager import manage_actions
from rorapp.actions.ready import ReadyAction
from rorapp.actions.ready_not import ReadyNotAction
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.models import AvailableAction, Game


READINESS_PHASES = [
    (Game.Phase.REVENUE, Game.SubPhase.REDISTRIBUTION),
    (Game.Phase.REVOLUTION, Game.SubPhase.CARD_TRADING),
]


def _action_names(game: Game, faction_id: int) -> set[str]:
    return set(
        AvailableAction.objects.filter(game=game, faction_id=faction_id).values_list(
            "base_name", flat=True
        )
    )


@pytest.mark.django_db
@pytest.mark.parametrize(("phase", "sub_phase"), READINESS_PHASES)
def test_ready_actions_are_used_for_simultaneous_phases(
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
    manage_actions(game.id)

    # Assert
    action_names = _action_names(game, faction.id)
    assert ReadyAction.NAME in action_names
    assert ReadyNotAction.NAME not in action_names
    assert DoneAction.NAME not in action_names

    ready_action = AvailableAction.objects.get(
        game=game, faction=faction, base_name=ReadyAction.NAME
    )
    assert ready_action.variant_name is None
    assert ready_action.name == "Ready"

    # Act
    result = ReadyAction().execute(game.id, faction.id, {}, FakeRandomResolver())
    manage_actions(game.id)

    # Assert
    assert result.success
    faction.refresh_from_db()
    assert faction.has_status_item(FactionStatusItem.DONE)

    action_names = _action_names(game, faction.id)
    assert ReadyAction.NAME not in action_names
    assert ReadyNotAction.NAME in action_names
    assert DoneAction.NAME not in action_names

    not_ready_action = AvailableAction.objects.get(
        game=game, faction=faction, base_name=ReadyNotAction.NAME
    )
    assert not_ready_action.variant_name is None
    assert not_ready_action.name == "Not ready"

    # Act
    result = ReadyNotAction().execute(game.id, faction.id, {}, FakeRandomResolver())

    # Assert
    assert result.success
    faction.refresh_from_db()
    assert not faction.has_status_item(FactionStatusItem.DONE)


@pytest.mark.django_db
@pytest.mark.parametrize("phase", [Game.Phase.INITIAL, Game.Phase.REVOLUTION])
def test_done_action_is_reserved_for_sequential_play_cards(
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
    manage_actions(game.id)

    # Assert
    action_names = _action_names(game, faction.id)
    assert DoneAction.NAME in action_names
    assert ReadyAction.NAME not in action_names
    assert ReadyNotAction.NAME not in action_names

    done_action = AvailableAction.objects.get(
        game=game, faction=faction, base_name=DoneAction.NAME
    )
    assert done_action.variant_name is None
    assert done_action.name == "Done"
