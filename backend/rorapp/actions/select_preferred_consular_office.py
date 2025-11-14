from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class SelectPreferredConsularOfficeAction(ActionBase):
    NAME = "Select preferred consular office"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.CONSULAR_ELECTION
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and len(
                [
                    s
                    for s in game_state.senators
                    if s.faction
                    and s.faction.id == faction.id
                    and s.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
                ]
            )
            == 1
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return None
        consul = [
            s
            for s in snapshot.senators
            if s.faction
            and s.faction.id == faction.id
            and s.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
        ][0]
        return AvailableAction.objects.create(
            game=snapshot.game,
            faction=faction,
            name=self.NAME,
            position=self.POSITION,
            schema=[
                {
                    "type": "select",
                    "name": consul.display_name,
                    "options": [
                        {
                            "value": "Rome Consul",
                            "name": "Rome Consul",
                        },
                        {
                            "value": "Field Consul",
                            "name": "Field Consul",
                        },
                    ],
                }
            ],
        )

    def execute(
        self, game_id: int, faction_id: int, selection: Dict[str, str]
    ) -> ExecutionResult:

        senator = [
            s
            for s in Senator.objects.filter(game=game_id, faction=faction_id)
            if s.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
        ][0]
        preferred_office = selection[senator.display_name]
        if preferred_office == "Rome Consul":
            senator.remove_status_item(Senator.StatusItem.PREFERS_FIELD_CONSUL)
            senator.add_status_item(Senator.StatusItem.PREFERS_ROME_CONSUL)
        else:
            senator.remove_status_item(Senator.StatusItem.PREFERS_ROME_CONSUL)
            senator.add_status_item(Senator.StatusItem.PREFERS_FIELD_CONSUL)

        return ExecutionResult(True)
