from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.end_prosecutions import end_prosecutions
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class CloseProsecutionsAction(ActionBase):
    NAME = "Close prosecutions"
    POSITION = 2

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        censor = next(
            (s for s in game_state.senators if s.has_title(Senator.Title.CENSOR)),
            None,
        )
        if not censor:
            return None

        if (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.PROSECUTION
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and censor.has_title(Senator.Title.PRESIDING_MAGISTRATE)
            and censor.faction
            and censor.faction.id == faction.id
            and not any(
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
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

        Log.create_object(game_id, "The Censor closed prosecutions.")
        end_prosecutions(game_id)
        return ExecutionResult(True)
