from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.governor_election import governor_consent_pending
from rorapp.helpers.text import format_list
from rorapp.models import AvailableAction, Faction, Log, Senator


class AcceptGovernorshipAction(ActionBase):
    NAME = "Accept governorship"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if faction and governor_consent_pending(
            game_state.game.current_proposal or "", game_state.senators, faction_id
        ):
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
        faction = Faction.objects.get(game=game_id, id=faction_id)
        accepted = [
            senator
            for senator in faction.senators.all()
            if senator.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
        ]
        if not accepted:
            return ExecutionResult(False, "No senator has been asked to consent.")

        for senator in accepted:
            senator.remove_status_item(Senator.StatusItem.CONSENT_REQUIRED)
            senator.save()
        Log.create_object(
            game_id,
            f"{format_list([s.display_name for s in accepted])} agreed to govern again.",
        )
        return ExecutionResult(True)
