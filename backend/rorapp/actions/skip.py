from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game


class SkipAction(ActionBase):
    NAME = "Skip"
    POSITION = 2

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if faction and (
            game_state.game.phase == Game.Phase.FORUM
            and (
                (
                    faction.has_status_item(Faction.StatusItem.CURRENT_INITIATIVE)
                    and (
                        game_state.game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT
                        or (
                            game_state.game.sub_phase == Game.SubPhase.SPONSOR_GAMES
                            and any(
                                s.talents >= 7
                                for s in game_state.senators
                                if s.faction and s.faction.id == faction.id and s.alive
                            )
                        )
                    )
                )
                or (
                    game_state.game.sub_phase == Game.SubPhase.INITIATIVE_AUCTION
                    and faction.has_status_item(Faction.StatusItem.CURRENT_BIDDER)
                )
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                position=self.POSITION,
                schema=[],
            )
        return None

    def execute(
        self, game_id: int, faction_id: int, selection: Dict[str, str]
    ) -> ExecutionResult:
        game = Game.objects.get(id=game_id)
        if game.sub_phase == Game.SubPhase.ATTRACT_KNIGHT:
            game.sub_phase = Game.SubPhase.SPONSOR_GAMES
        elif game.sub_phase == Game.SubPhase.SPONSOR_GAMES:
            game.sub_phase = Game.SubPhase.FACTION_LEADER
        elif game.sub_phase == Game.SubPhase.INITIATIVE_AUCTION:
            faction = Faction.objects.get(game=game_id, id=faction_id)
            faction.add_status_item(Faction.StatusItem.SKIPPED)
        game.save()
        return ExecutionResult(True)
