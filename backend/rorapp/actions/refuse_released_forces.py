from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.actions.pay_for_released_forces import hrao_faction
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.rebel_maintenance import released_legions
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Faction, Log


class RefuseReleasedForcesAction(ActionBase):
    NAME = "Refuse released forces"
    POSITION = 6

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        return hrao_faction(game_state, faction_id)

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        legions = released_legions(game_id)
        if not legions:
            return ExecutionResult(False, "There are no released forces.")

        Log.create_object(
            game_id,
            f"The Senate refused {unit_list_to_string(legions, [])} released "
            f"by the rebels, and {'they were' if len(legions) > 1 else 'it was'} "
            "eliminated.",
        )
        for legion in legions:
            legion.delete()
        return ExecutionResult(True)
