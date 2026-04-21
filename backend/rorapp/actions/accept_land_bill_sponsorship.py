from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.text import format_list
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class AcceptLandBillSponsorshipAction(ActionBase):
    NAME = "Accept land bill sponsorship"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        proposal = game_state.game.current_proposal or ""
        if (
            game_state.game.sub_phase != Game.SubPhase.OTHER_BUSINESS
            or not proposal.startswith("Pass type ")
        ):
            return None
        faction = game_state.get_faction(faction_id)
        if faction and any(
            s
            for s in game_state.senators
            if s.faction
            and s.faction.id == faction.id
            and s.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            return [
                AvailableAction.objects.create(
                    game=snapshot.game,
                    faction=faction,
                    base_name=self.NAME,
                    position=self.POSITION,
                    schema=[],
                )
            ]
        return []

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        faction = Faction.objects.get(game=game_id, id=faction_id)
        accepted = []
        for senator in faction.senators.all():
            if senator.has_status_item(Senator.StatusItem.CONSENT_REQUIRED):
                senator.remove_status_item(Senator.StatusItem.CONSENT_REQUIRED)
                senator.save()
                accepted.append(senator)
        if accepted:
            names = format_list([s.display_name for s in accepted])
            Log.create_object(game_id, f"{names} agreed to sponsor the land bill.")
        return ExecutionResult(True)
