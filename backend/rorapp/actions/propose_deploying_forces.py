from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class ProposeDeployingForcesAction(ActionBase):
    NAME = "Propose deploying forces"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.OTHER_BUSINESS
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
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            available_commanders = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction
                    and s.alive
                    and (
                        s.has_title(Senator.Title.ROME_CONSUL)
                        or s.has_title(Senator.Title.FIELD_CONSUL)
                    )
                ],
                key=lambda s: s.name,
            )
            if len(available_commanders) > 1:
                available_commanders = [
                    s
                    for s in available_commanders
                    if s.has_title(Senator.Title.FIELD_CONSUL)
                ]

            # TODO limit this to only legions in Rome
            available_legions = snapshot.legions
            available_fleets = snapshot.fleets

            target_wars = sorted(snapshot.wars, key=lambda w: w.id)

            return AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Commander",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                                "signals": {"commander_strength": s.military},
                            }
                            for s in available_commanders
                        ],
                    },
                    {
                        "type": "select",
                        "name": "Target war",
                        "options": [
                            {
                                "value": w.id,
                                "object_class": "war",
                                "id": w.id,
                                "signals": {
                                    "war_strength": (
                                        w.land_strength
                                        if w.naval_strength == 0
                                        else w.naval_strength
                                    ),
                                    "disaster_num_1": (
                                        w.disaster_numbers[0]
                                        if len(w.disaster_numbers) > 0
                                        else 0
                                    ),
                                    "disaster_num_2": (
                                        w.disaster_numbers[1]
                                        if len(w.disaster_numbers) > 1
                                        else 0
                                    ),
                                    "standoff_num_1": (
                                        w.standoff_numbers[0]
                                        if len(w.standoff_numbers) > 0
                                        else 0
                                    ),
                                    "standoff_num_2": (
                                        w.standoff_numbers[1]
                                        if len(w.standoff_numbers) > 1
                                        else 0
                                    ),
                                    "battle_type": (
                                        "land" if w.naval_strength == 0 else "naval"
                                    ),
                                },
                            }
                            for w in target_wars
                        ],
                        "inline": True,
                    },
                    {
                        "type": "multiselect",
                        "name": "Legions",
                        "options": [
                            {
                                "value": l.id,
                                "object_class": "legion",
                                "id": l.id,
                                "signals": {"legion_strength": l.strength},
                            }
                            for l in available_legions
                        ],
                    },
                    {
                        "type": "multiselect",
                        "name": "Fleets",
                        "options": [
                            {
                                "value": f.id,
                                "object_class": "fleet",
                                "id": f.id,
                            }
                            for f in available_fleets
                        ],
                        "inline": True,
                    },
                    {
                        "type": "info",
                        "conditions": [
                            {
                                "value1": "signal:battle_type",
                                "operation": "==",
                                "value2": "land",
                                "text": "Selected legions will engage in a land battle.",
                            },
                            {
                                "value1": "signal:battle_type",
                                "operation": "==",
                                "value2": "naval",
                                "text": "Selected fleets will engage in a naval battle.",
                            },
                        ],
                    },
                    {
                        "type": "calculation",
                        "name": "Roman strength",
                        "value": "signal:commander_strength + signal:legion_strength",
                    },
                    {
                        "type": "calculation",
                        "name": "Opposing strength (minimum force)",
                        "value": "signal:war_strength",
                    },
                    {
                        "type": "chance",
                        "name": "Chance of victory",
                        "dice": 3,
                        "target_min": 14,
                        "modifiers": [
                            "signal:commander_strength",
                            "signal:legion_strength",
                            "-1 * signal:war_strength",
                        ],
                        "ignored_numbers": [
                            "signal:disaster_num_1",
                            "signal:disaster_num_2",
                            "signal:standoff_num_1",
                            "signal:standoff_num_2",
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of stalemate",
                        "dice": 3,
                        "target_min": 8,
                        "target_max": 13,
                        "modifiers": [
                            "signal:commander_strength",
                            "signal:legion_strength",
                            "-1 * signal:war_strength",
                        ],
                        "ignored_numbers": [
                            "signal:disaster_num_1",
                            "signal:disaster_num_2",
                            "signal:standoff_num_1",
                            "signal:standoff_num_2",
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of defeat",
                        "dice": 3,
                        "target_max": 7,
                        "modifiers": [
                            "signal:commander_strength",
                            "signal:legion_strength",
                            "-1 * signal:war_strength",
                        ],
                        "ignored_numbers": [
                            "signal:disaster_num_1",
                            "signal:disaster_num_2",
                            "signal:standoff_num_1",
                            "signal:standoff_num_2",
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of standoff",
                        "dice": 3,
                        "target_exacts": [
                            "signal:standoff_num_1",
                            "signal:standoff_num_2",
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of disaster",
                        "dice": 3,
                        "target_exacts": [
                            "signal:disaster_num_1",
                            "signal:disaster_num_2",
                        ],
                    },
                ],
            )
        return None

    def execute(
        self, game_id: int, faction_id: int, selection: Dict[str, str]
    ) -> ExecutionResult:

        return ExecutionResult(True)
