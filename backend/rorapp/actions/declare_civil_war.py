from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import (
    declare_civil_war,
    declaring_faction,
    next_land_victor,
    revolt_available,
)
from rorapp.models import AvailableAction, Faction


class DeclareCivilWarAction(ActionBase):
    NAME = "Declare civil war"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = declaring_faction(game_state, faction_id)
        if not faction:
            return None
        campaign = next_land_victor(faction.game_id)
        if not campaign or not revolt_available(campaign):
            return None
        return faction

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
            return ExecutionResult(False, "There is no command to revolt with.")
        if campaign.commander.faction_id != faction_id:
            return ExecutionResult(False, "It is not your commander's decision.")
        if not revolt_available(campaign):
            return ExecutionResult(
                False, "Another faction is already in revolt with a stronger army."
            )

        declare_civil_war(campaign)
        return ExecutionResult(True)
