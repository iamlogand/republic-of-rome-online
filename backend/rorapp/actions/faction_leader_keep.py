from typing import Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator


class FactionLeaderKeepAction(ActionBase):
    NAME = "Keep faction leader"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.FACTION_LEADER
            and faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE)
            and any(
                s.has_title(Senator.Title.FACTION_LEADER)
                for s in game_state.senators
                if s.faction and s.faction.id == faction_id and s.alive
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
        selection: Dict[str, str],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        # End initiative
        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.remove_status_item(FactionStatusItem.CURRENT_INITIATIVE)
        faction.save()
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.END
        game.save()

        return ExecutionResult(True)
