from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import (
    deciding_senator,
    get_civil_war,
    may_join_the_revolt,
)
from rorapp.models import AvailableAction, Faction, Log


class JoinTheRevoltAction(ActionBase):
    NAME = "Join the revolt"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        senator = deciding_senator(game_state, faction_id)
        if not senator or not may_join_the_revolt(senator):
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
                variant_name=f"{senator.display_name} joins the revolt",
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
        senator = deciding_senator(GameStateLive(game_id), faction_id)
        if not senator:
            return ExecutionResult(False, "There is no loyalty to declare.")
        if not may_join_the_revolt(senator):
            return ExecutionResult(
                False, "The Master of Horse may only join a rebel Dictator."
            )

        senator.rebel = True
        senator.save()

        war = get_civil_war(game_id)
        rebel_name = (
            war.primary_rebel.display_name if war and war.primary_rebel else "the rebel"
        )
        Log.create_object(
            game_id,
            f"{senator.display_name} joined {rebel_name} in revolt.",
        )
        return ExecutionResult(True)
