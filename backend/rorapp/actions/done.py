from typing import List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction


class DoneAction(ActionBase):
    NAME = "Done"

    def validate(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and "done" not in faction.status
            and (
                game_state.game.phase == "revenue"
                and game_state.game.sub_phase == "redistribution"
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:
        faction = self.validate(snapshot, faction_id)
        if faction:
            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                schema=[],
            )
        return None

    def execute(self, game_id: int, faction_id: int, selection: List) -> bool:
        game_state = GameStateLive(game_id)
        faction = self.validate(game_state, faction_id)
        if faction:
            faction.status.append("done")
            faction.save()
            game_state.game.increment_step()
            return True
        return False
