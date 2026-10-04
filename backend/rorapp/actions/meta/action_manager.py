from typing import Dict, List, Type

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.registry import action_registry
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction
from rorapp.models.game import Game
from rorapp.models.pending_decision import PendingDecision


def manage_actions(game_id: int) -> None:
    snapshot = GameStateSnapshot(game_id)

    actions: List[Type[ActionBase]] = action_registry

    available_actions: List[AvailableAction] = []
    pending_decisions: Dict[int, tuple[int, PendingDecision]] = {}
    if snapshot.game.finished_on is None:
        for action_cls in actions:
            action = action_cls()
            for faction in snapshot.factions:
                actions_for_faction = action.get_schema(snapshot, faction.id)
                available_actions.extend(actions_for_faction)

                if actions_for_faction:
                    current = pending_decisions.get(faction.id)
                    if current is None or action.POSITION < current[0]:
                        description = action.get_pending_decision(snapshot, faction.id)
                        if description is not None:
                            pending_decisions[faction.id] = (
                                action.POSITION,
                                PendingDecision(
                                    game=snapshot.game,
                                    faction=faction,
                                    description=description,
                                ),
                            )

    AvailableAction.objects.filter(game=snapshot.game).delete()
    if available_actions:
        AvailableAction.objects.bulk_create(available_actions)

    PendingDecision.objects.filter(game=snapshot.game).delete()
    if pending_decisions:
        PendingDecision.objects.bulk_create(
            [pd for _, pd in pending_decisions.values()]
        )

    game = Game.objects.get(id=game_id)
    game.step += 1
    game.save()
