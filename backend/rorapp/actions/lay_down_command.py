from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import declaring_faction, next_land_victor
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.models import AvailableAction, Faction


class LayDownCommandAction(ActionBase):
    NAME = "Lay down command"
    POSITION = 6

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        return declaring_faction(game_state, faction_id)

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
        campaign = next_land_victor(game_id)
        if not campaign or not campaign.commander:
            return ExecutionResult(False, "There is no command to lay down.")
        if campaign.commander.faction_id != faction_id:
            return ExecutionResult(False, "It is not your commander's decision.")

        lay_down_command(campaign)
        return ExecutionResult(True)
