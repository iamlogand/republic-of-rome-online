from typing import Any, Dict, List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.senate_proposal import any_proposal_available
from rorapp.helpers.tribune import faction_has_tribune, spend_tribune
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class PlayTribuneAction(ActionBase):
    NAME = "Propose with tribune"
    POSITION = 101

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        if game_state.game.phase != Game.Phase.SENATE:
            return None

        allowed_sub_phases = {
            Game.SubPhase.CONSULAR_ELECTION,
            Game.SubPhase.CENSOR_ELECTION,
            Game.SubPhase.DICTATOR_ELECTION,
            Game.SubPhase.OTHER_BUSINESS,
        }
        if game_state.game.sub_phase not in allowed_sub_phases:
            return None

        if not faction_has_tribune(faction, game_state.senators):
            return None

        if any(
            f.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
            for f in game_state.factions
        ):
            return None

        if any(
            s.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
            for s in game_state.senators
        ):
            return None

        if not any_proposal_available(game_state):
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
        senators = list(Senator.objects.filter(game=game_id, faction=faction_id))

        if not faction_has_tribune(faction, senators):
            return ExecutionResult(False, "No tribune available.")

        spend_tribune(game_id, faction_id)

        faction.refresh_from_db()
        faction.add_status_item(FactionStatusItem.PLAYED_TRIBUNE)
        faction.save()

        Log.create_object(
            game_id,
            f"{faction.display_name} played a tribune to propose the next motion.",
        )

        return ExecutionResult(True)
