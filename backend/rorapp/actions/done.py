from typing import Dict, List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.helpers.get_next_faction_in_order import get_next_faction_in_order
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game


class DoneAction(ActionBase):
    NAME = "Done"
    POSITION = 2

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and not faction.has_status_item(FactionStatusItem.DONE)
            and (
                (
                    game_state.game.phase == Game.Phase.REVENUE
                    and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
                )
                or (
                    game_state.game.phase == Game.Phase.REVOLUTION
                    and game_state.game.sub_phase
                    == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
                    and faction.has_status_item(FactionStatusItem.MAKING_DECISION)
                )
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
        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.add_status_item(FactionStatusItem.DONE)
        faction.remove_status_item(FactionStatusItem.MAKING_DECISION)
        faction.save()

        game = Game.objects.get(id=game_id)

        if (
            game.phase == Game.Phase.REVOLUTION
            and game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
        ):
            # Figure out which faction is next
            factions = Faction.objects.filter(game=game_id)
            next_faction = get_next_faction_in_order(factions, faction.position)
            
            if not next_faction.has_status_item(FactionStatusItem.DONE):
                next_faction.add_status_item(FactionStatusItem.MAKING_DECISION)
                next_faction.save()

        return ExecutionResult(True)
