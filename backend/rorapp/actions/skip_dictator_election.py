from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.pending_decision_description import PendingDecisionDescription
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class SkipDictatorElectionAction(ActionBase):
    NAME = "Skip"
    POSITION = 101

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.DICTATOR_ELECTION
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and any(
                s
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
            )
            and not any(
                f
                for f in game_state.factions
                if f.id != faction.id
                and f.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
            )
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
                    field_descriptors=[],
                )
            ]
        return []

    def get_pending_decision(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[str]:
        return PendingDecisionDescription.NOMINATE_DICTATOR

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.remove_status_item(FactionStatusItem.PLAYED_TRIBUNE)
        faction.save()
        factions = list(Faction.objects.filter(game=game_id))
        for f in factions:
            f.remove_status_item(FactionStatusItem.PROPOSED_VIA_TRIBUNE)
        Faction.objects.bulk_update(factions, ["status_items"])
        Log.create_object(
            game_id,
            "The presiding magistrate declined to call for a Dictator election.",
        )
        game.sub_phase = Game.SubPhase.CENSOR_ELECTION
        game.clear_senate_sub_phase_proposals()
        game.save()
        return ExecutionResult(True)
