from typing import List, Type

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.registry import action_registry
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction
from rorapp.models.game import Game


def manage_actions(game_id: int) -> None:
    snapshot = GameStateSnapshot(game_id)

    actions: List[Type[ActionBase]] = list(action_registry.values())

    available_actions: List[AvailableAction] = []
    if snapshot.game.finished_on is None:
        for action_cls in actions:
            action = action_cls()
            for faction in snapshot.factions:
                actions_for_faction = action.get_schema(snapshot, faction.id)
                available_actions.extend(actions_for_faction)

    AvailableAction.objects.filter(game=snapshot.game).delete()
    if len(available_actions) > 0:
        AvailableAction.objects.bulk_create(available_actions)

    game = Game.objects.get(id=game_id)
    game.step += 1
    game.save()
