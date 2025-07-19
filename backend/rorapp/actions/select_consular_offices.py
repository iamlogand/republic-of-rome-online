from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.transfer_power_consuls import transfer_power_consuls
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class SelectConsularOfficesAction(ActionBase):
    NAME = "Select consular offices"
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
            == 2
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            consuls = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction
                    and s.faction.id == faction.id
                    and s.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
                ],
                key=lambda s: s.name,
            )
            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": consuls[0].display_name,
                        "options": [
                            {
                                "value": "Rome Consul",
                                "name": "Rome Consul",
                                "signals": {
                                    "first_title": "Rome Consul",
                                },
                            },
                            {
                                "value": "Field Consul",
                                "name": "Field Consul",
                                "signals": {
                                    "first_title": "Field Consul",
                                },
                            },
                        ],
                    },
                    {
                        "type": "select",
                        "name": consuls[1].display_name,
                        "options": [
                            {
                                "value": "Rome Consul",
                                "name": "Rome Consul",
                                "conditions": [
                                    {
                                        "value1": "signal:first_title",
                                        "operation": "!=",
                                        "value2": "Rome Consul",
                                    },
                                ],
                            },
                            {
                                "value": "Field Consul",
                                "name": "Field Consul",
                                "conditions": [
                                    {
                                        "value1": "signal:first_title",
                                        "operation": "!=",
                                        "value2": "Field Consul",
                                    },
                                ],
                            },
                        ],
                    },
                ],
            )
        return None

    def execute(
        self, game_id: int, faction_id: int, selection: Dict[str, str]
    ) -> ExecutionResult:

        senators = Senator.objects.filter(game=game_id, alive=True)

        consuls = [
            s for s in senators if s.has_status_item(Senator.StatusItem.INCOMING_CONSUL)
        ]
        rome_consul: Optional[Senator] = None
        field_consul: Optional[Senator] = None
        for consul in consuls:
            selected_office = selection[consul.display_name]
            if selected_office == "Rome Consul":
                rome_consul = consul
            else:
                field_consul = consul

        if (
            not rome_consul
            or not field_consul
            or selection[rome_consul.display_name] != "Rome Consul"
            or selection[field_consul.display_name] != "Field Consul"
        ):
            return ExecutionResult(False)

        Log.create_object(
            game_id,
            f"{rome_consul.display_name} agreed to be Rome Consul and {field_consul.display_name} agreed to be Field Consul.",
        )

        result = transfer_power_consuls(game_id, rome_consul.id, field_consul.id)

        return ExecutionResult(result)
