from typing import Any, Dict, List, Optional

from rorapp.actions.join_the_revolt import deciding_senator
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import undecided_secondary_rebels
from rorapp.models import AvailableAction, Faction, Senator


class RemainLoyalAction(ActionBase):
    NAME = "Remain loyal"
    POSITION = 6

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        if not deciding_senator(game_state, faction_id):
            return None
        return game_state.get_faction(faction_id)

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        senator = deciding_senator(snapshot, faction_id)
        if not faction or not senator:
            return []
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                variant_name=f"{senator.display_name} remains loyal",
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
        undecided = undecided_secondary_rebels(game_id)
        if not undecided or undecided[0].faction_id != faction_id:
            return ExecutionResult(False, "There is no loyalty to declare.")
        senator = undecided[0]

        senator.add_status_item(Senator.StatusItem.REMAINED_LOYAL)
        senator.save()
        return ExecutionResult(True)
