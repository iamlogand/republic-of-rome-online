from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game


class NotDoneAction(ActionBase):
    NAME = "Not done"
    POSITION = 2

    def validate(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and faction.has_status_item(Faction.StatusItem.DONE)
            and (
                game_state.game.phase == Game.Phase.REVENUE
                and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
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
                position=self.POSITION,
                schema=[],
            )
        return None

    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:
        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.remove_status_item(Faction.StatusItem.DONE)
        faction.save()
        return True
