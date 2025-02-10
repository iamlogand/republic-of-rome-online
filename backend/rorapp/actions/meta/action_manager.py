from typing import List, Type

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.action_registry import action_registry
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction


def manage_actions(game_id: int) -> None:
    snapshot = GameStateSnapshot(game_id)
    actions: List[Type[ActionBase]] = list(action_registry.values())

    available_actions: List = []
    for action_cls in actions:
        action_instance: ActionBase = action_cls()
        for faction in snapshot.factions:
            available_action = action_instance.get_schema(snapshot, faction.id)
            if available_action:
                available_actions.append(available_action)

    AvailableAction.objects.filter(game=snapshot.game).delete()
    if len(available_actions) > 0:
        AvailableAction.objects.bulk_create(available_actions)
