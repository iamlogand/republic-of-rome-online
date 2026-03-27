from typing import Any, Dict, List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Log


class CancelTribuneAction(ActionBase):
    NAME = "Cancel tribune"
    POSITION = 101

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        if not faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE):
            return None

        proposal_on_floor = bool(
            game_state.game.current_proposal
            and game_state.game.current_proposal.strip()
        )
        if proposal_on_floor:
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

        faction = Faction.objects.get(game=game_id, id=faction_id)

        if not faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE):
            return ExecutionResult(False, "No tribune has been played.")

        faction.remove_status_item(FactionStatusItem.PLAYED_TRIBUNE)
        faction.save()

        Log.create_object(game_id, f"{faction.display_name} cancelled their tribune.")

        return ExecutionResult(True)
