from typing import Any, Dict, List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Log, Senator


class Lose1Influence(ActionBase):
    NAME = "Lose 1 influence"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        pm_senator = next(
            (
                s
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
            ),
            None,
        )
        if pm_senator and pm_senator.influence > 0:
            return faction
        return None

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
                schema=[],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        pm_senator = next(
            (
                s
                for s in Senator.objects.filter(game=game_id)
                if s.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
            ),
            None,
        )
        if not pm_senator:
            return ExecutionResult(False, "No unanimous defeat pending.")
        if pm_senator.influence == 0:
            return ExecutionResult(False, "Senator has no influence to lose.")

        pm_senator.influence -= 1
        pm_senator.remove_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
        pm_senator.save()

        Log.create_object(
            game_id,
            f"{pm_senator.display_name} decided to lose 1 influence.",
        )

        return ExecutionResult(True)
