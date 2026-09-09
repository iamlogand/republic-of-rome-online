from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.repopulation import (
    SENATORS_REQUIRED_IN_ROME,
    unaligned_senators_in_rome,
)
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class SelectSenatorAction(ActionBase):
    NAME = "Select senator"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if game_state.game.phase != Game.Phase.SENATE:
            return None
        if game_state.game.sub_phase != Game.SubPhase.REPOPULATION:
            return None
        if not faction.has_status_item(FactionStatusItem.AWAITING_DECISION):
            return None
        if not unaligned_senators_in_rome(game_state.senators):
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        candidates = sorted(
            unaligned_senators_in_rome(snapshot.senators),
            key=lambda senator: senator.family_name,
        )

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {
                        "type": "select",
                        "name": "Senator",
                        "options": [
                            {
                                "value": senator.id,
                                "object_class": "senator",
                                "id": senator.id,
                            }
                            for senator in candidates
                        ],
                    }
                ],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(id=faction_id)
        senator = Senator.objects.get(id=selection["Senator"])

        if not senator.alive or senator.faction_id:
            return ExecutionResult(False, "Senator is not available.")

        senator.faction = faction
        senator.save()

        Log.create_object(
            game_id,
            f"With fewer than {SENATORS_REQUIRED_IN_ROME} aligned senators in Rome, "
            f"{senator.display_name} joined {faction.display_name}.",
        )

        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()

        game.sub_phase = game.interrupted_sub_phase
        game.interrupted_sub_phase = ""
        game.save()

        return ExecutionResult(True)
