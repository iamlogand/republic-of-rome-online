from typing import Any, Dict, List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.unanimous_defeat import step_down_by_choice
from rorapp.models import AvailableAction, Faction, Senator


class StepDownAsPresidingMagistrateAction(ActionBase):
    NAME = "Step down as presiding magistrate"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        presiding_magistrate = next(
            (
                s
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
            ),
            None,
        )
        return faction if presiding_magistrate else None

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

        presiding_magistrate = next(
            (
                s
                for s in Senator.objects.filter(game=game_id)
                if s.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
            ),
            None,
        )
        if not presiding_magistrate:
            return ExecutionResult(False, "No unanimous defeat pending.")

        step_down_by_choice(game_id, presiding_magistrate.id)
        return ExecutionResult(True)
