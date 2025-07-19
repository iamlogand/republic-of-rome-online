from typing import Dict, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import (
    AvailableAction,
    Campaign,
    Faction,
    Fleet,
    Game,
    Legion,
    Log,
    Senator,
    War,
)
from rorapp.helpers.unit_lists import unit_list_to_string


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
            available_commanders = [
                s
                for s in game_state.senators
                if s.faction
                and s.alive
                and (
                    s.has_title(Senator.Title.ROME_CONSUL)
                    or s.has_title(Senator.Title.FIELD_CONSUL)
                )
                and not any(c.commander.id == s.id for c in game_state.campaigns)
                and not any(
                    c.master_of_horse and c.master_of_horse.id == s.id
                    for c in game_state.campaigns
                )
            ]
            if len(available_commanders) == 0:
                return None

            available_legions = [l for l in game_state.legions if l.campaign is None]
            available_fleets = [f for f in game_state.fleets if f.campaign is None]
            if len(available_legions) + len(available_fleets) > 0:
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
                    and not any(c.commander.id == s.id for c in snapshot.campaigns)
                    and s.location == "Rome"
                ],
                key=lambda s: s.name,
            )
            if len(available_commanders) > 1:
                available_commanders = [
                    s
                    for s in available_commanders
                    if s.has_title(Senator.Title.FIELD_CONSUL)
                ]

            available_legions = [l for l in snapshot.legions if l.campaign is None]
            available_fleets = [f for f in snapshot.fleets if f.campaign is None]

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
                                    "initial_battle": (
                                        "land" if w.naval_strength == 0 else "naval"
                                    ),
                                    "fleet_support": (w.fleet_support),
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
                                "signals": {"fleet_strength": 1},
                            }
                            for f in available_fleets
                        ],
                        "inline": True,
                    },
                    {
                        "type": "calculation",
                        "name": "Insufficient fleet support",
                        "label": "HIDDEN",
                        "value": "Insufficient fleet support",
                        "conditions": [
                            {
                                "value1": "signal:fleet_strength",
                                "operation": "<",
                                "value2": "signal:fleet_support",
                            },
                        ],
                        "style": "warning",
                    },
                    {
                        "type": "calculation",
                        "name": "Minimum force land",
                        "label": "HIDDEN",
                        "value": "Commander consent required (not enough legions)",
                        "conditions": [
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "land",
                            },
                            {
                                "value1": "signal:commander_strength + signal:legion_strength",
                                "operation": "<",
                                "value2": "signal:war_strength",
                            },
                        ],
                        "style": "warning",
                    },
                    {
                        "type": "calculation",
                        "name": "Minimum force fleet",
                        "label": "HIDDEN",
                        "value": "Commander consent required (not enough fleets)",
                        "conditions": [
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "naval",
                            },
                            {
                                "value1": "signal:commander_strength + signal:fleet_strength",
                                "operation": "<",
                                "value2": "signal:war_strength",
                            },
                        ],
                        "style": "warning",
                    },
                    {
                        "type": "calculation",
                        "name": "Land battle",
                        "label": "HIDDEN",
                        "value": "Land battle",
                        "conditions": [
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "land",
                            }
                        ],
                    },
                    {
                        "type": "calculation",
                        "name": "naval battle",
                        "label": "HIDDEN",
                        "value": "Naval battle (undefeated enemy navy)",
                        "conditions": [
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "naval",
                            }
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of victory land",
                        "label": "Chance of victory",
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
                        "conditions": [
                            {
                                "value1": "signal:war_strength",
                                "operation": "!=",
                                "value2": "0",
                            },
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "land",
                            },
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of victory naval",
                        "label": "Chance of victory",
                        "dice": 3,
                        "target_min": 14,
                        "modifiers": [
                            "signal:commander_strength",
                            "signal:fleet_strength",
                            "-1 * signal:war_strength",
                        ],
                        "ignored_numbers": [
                            "signal:disaster_num_1",
                            "signal:disaster_num_2",
                            "signal:standoff_num_1",
                            "signal:standoff_num_2",
                        ],
                        "conditions": [
                            {
                                "value1": "signal:war_strength",
                                "operation": "!=",
                                "value2": "0",
                            },
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "naval",
                            },
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of stalemate land",
                        "label": "Chance of stalemate",
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
                        "conditions": [
                            {
                                "value1": "signal:war_strength",
                                "operation": "!=",
                                "value2": "0",
                            },
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "land",
                            },
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of stalemate naval",
                        "label": "Chance of stalemate",
                        "dice": 3,
                        "target_min": 8,
                        "target_max": 13,
                        "modifiers": [
                            "signal:commander_strength",
                            "signal:fleet_strength",
                            "-1 * signal:war_strength",
                        ],
                        "ignored_numbers": [
                            "signal:disaster_num_1",
                            "signal:disaster_num_2",
                            "signal:standoff_num_1",
                            "signal:standoff_num_2",
                        ],
                        "conditions": [
                            {
                                "value1": "signal:war_strength",
                                "operation": "!=",
                                "value2": "0",
                            },
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "naval",
                            },
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of defeat land",
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
                        "conditions": [
                            {
                                "value1": "signal:war_strength",
                                "operation": "!=",
                                "value2": "0",
                            },
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "land",
                            },
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance of defeat naval",
                        "name": "Chance of defeat",
                        "dice": 3,
                        "target_max": 7,
                        "modifiers": [
                            "signal:commander_strength",
                            "signal:fleet_strength",
                            "-1 * signal:war_strength",
                        ],
                        "ignored_numbers": [
                            "signal:disaster_num_1",
                            "signal:disaster_num_2",
                            "signal:standoff_num_1",
                            "signal:standoff_num_2",
                        ],
                        "conditions": [
                            {
                                "value1": "signal:war_strength",
                                "operation": "!=",
                                "value2": "0",
                            },
                            {
                                "value1": "signal:initial_battle",
                                "operation": "==",
                                "value2": "naval",
                            },
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
                        "conditions": [
                            {
                                "value1": "signal:war_strength",
                                "operation": "!=",
                                "value2": "0",
                            },
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
                        "conditions": [
                            {
                                "value1": "signal:war_strength",
                                "operation": "!=",
                                "value2": "0",
                            },
                        ],
                    },
                ],
            )
        return None

    def execute(
        self, game_id: int, faction_id: int, selection: Dict[str, str]
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        if not faction:
            return ExecutionResult(False)

        # Retrieve and validate selection
        commander_id = selection["Commander"]
        commander = Senator.objects.get(game=game, id=commander_id)
        available_commanders = [
            s
            for s in Senator.objects.filter(
                game=game, alive=True, faction__isnull=False
            )
            if (
                s.has_title(Senator.Title.ROME_CONSUL)
                or s.has_title(Senator.Title.FIELD_CONSUL)
            )
            and s.location == "Rome"
        ]
        if len(available_commanders) > 1:
            available_commanders = [
                s
                for s in available_commanders
                if s.has_title(Senator.Title.FIELD_CONSUL)
            ]

        if commander.id not in [c.id for c in available_commanders]:
            return ExecutionResult(False, "Invalid commander selected")

        war_id = selection["Target war"]
        war = War.objects.get(game=game, id=war_id)

        legion_ids = selection["Legions"] if "Legions" in selection else []
        legions = Legion.objects.filter(game=game, id__in=legion_ids)
        if len(legion_ids) != len(legions):
            return ExecutionResult(False, "Invalid legions selected")

        fleet_ids = selection["Fleets"] if "Fleets" in selection else []
        fleets = Fleet.objects.filter(game=game, id__in=fleet_ids)
        if len(fleet_ids) != len(fleets):
            return ExecutionResult(False, "Invalid fleets selected")

        if war.fleet_support > len(fleets):
            return ExecutionResult(
                False, f"This war requires at least {war.fleet_support} fleet support"
            )

        if len(legions) + len(fleets) < 1:
            return ExecutionResult(False, "Select at least one legion or fleet")
        
        # Create consent required status if below minimum force
        force_strength = commander.military + sum(l.strength for l in legions) + len(fleets)
        minimum_force = war.naval_strength if war.naval_strength > 0 else war.land_strength
        if force_strength < minimum_force:
            commander.add_status_item(Senator.StatusItem.CONSENT_REQUIRED)
            commander.save()

        # Determine proposal
        proposal = f"Deploy {commander.display_name} with command of"
        if len(legions) > 0:
            legion_names = unit_list_to_string(list(legions))
            proposal += f" {len(legions)} {'legions' if len(legions) > 1 else 'legion'} ({legion_names})"
            if len(fleets) > 0:
                proposal += " and"
        if len(fleets) > 0:
            fleet_names = unit_list_to_string(list(fleets))
            proposal += f" {len(fleets)} {'fleets' if len(fleets) > 1 else 'fleet'} ({fleet_names})"
        proposal += f" to the {war.name}"

        # Validate proposal
        if proposal in game.defeated_proposals:
            return ExecutionResult(False, "This proposal was previously rejected")

        # Set current proposal
        game.current_proposal = proposal
        game.save()

        # Create log
        presiding_magistrate = [
            s
            for s in faction.senators.all()
            if s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
        ][0]
        Log.create_object(
            game_id,
            f"{presiding_magistrate.display_name} proposed the motion: {game.current_proposal}.",
        )

        return ExecutionResult(True)
