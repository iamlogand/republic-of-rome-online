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
                    or s.has_title(Senator.Title.PROCONSUL)
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
                        or s.has_title(Senator.Title.PROCONSUL)
                    )
                ],
                key=lambda s: s.name,
            )

            # Rome Consul can only be deployed if field consul has already been deployed
            field_consuls = [
                s
                for s in available_commanders
                if s.has_title(Senator.Title.FIELD_CONSUL)
            ]
            field_consul = field_consuls[0] if len(field_consuls) == 1 else None
            if field_consul and field_consul.location == "Rome":
                available_commanders = [
                    s
                    for s in available_commanders
                    if not s.has_title(Senator.Title.ROME_CONSUL)
                ]

            available_legions = sorted(
                [l for l in snapshot.legions if l.campaign is None],
                key=lambda l: l.number,
            )
            available_fleets = sorted(
                [f for f in snapshot.fleets if f.campaign is None],
                key=lambda f: f.number,
            )

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
                or s.has_title(Senator.Title.PROCONSUL)
            )
        ]

        # Rome Consul can only be deployed if field consul has already been deployed
        field_consuls = [
            s for s in available_commanders if s.has_title(Senator.Title.FIELD_CONSUL)
        ]
        field_consul = field_consuls[0] if len(field_consuls) == 1 else None
        if field_consul and field_consul.location == "Rome":
            available_commanders = [
                s
                for s in available_commanders
                if not s.has_title(Senator.Title.ROME_CONSUL)
            ]

        # Check if selected commander is available
        if commander.id not in [c.id for c in available_commanders]:
            return ExecutionResult(False, "Invalid commander selected")

        war_id = selection["Target war"]
        war = War.objects.get(game=game, id=war_id)

        commander_already_deployed = commander.location == war.location and (
            commander.has_title(Senator.Title.ROME_CONSUL)
            or commander.has_title(Senator.Title.FIELD_CONSUL)
            or commander.has_title(Senator.Title.PROCONSUL)
        )

        # Identify existing campaign that will merge with this one
        if commander_already_deployed:
            existing_campaigns = list(
                Campaign.objects.filter(game=game_id, war=war, commander=commander)
            )
            if len(existing_campaigns) == 0:
                return ExecutionResult(
                    False, "Commander is already deployed to another war"
                )
        else:
            existing_campaigns = list(
                Campaign.objects.filter(game=game_id, war=war, commander=None)
            )
        existing_campaign = (
            existing_campaigns[0] if len(existing_campaigns) == 1 else None
        )

        legion_ids = selection["Legions"] if "Legions" in selection else []
        legions = Legion.objects.filter(game=game, id__in=legion_ids).order_by("number")
        if len(legion_ids) != len(legions):
            return ExecutionResult(False, "Invalid legions selected")

        fleet_ids = selection["Fleets"] if "Fleets" in selection else []
        fleets = Fleet.objects.filter(game=game, id__in=fleet_ids).order_by("number")
        if len(fleet_ids) != len(fleets):
            return ExecutionResult(False, "Invalid fleets selected")

        if (
            commander.has_title(Senator.Title.PROCONSUL)
            and len(legions) + len(fleets) == 0
        ):
            return ExecutionResult(False, "No legions or fleets selected")

        naval_force = len(fleets)
        if existing_campaign:
            naval_force += existing_campaign.fleets.count()
        if war.fleet_support > naval_force:
            return ExecutionResult(
                False,
                f"Insufficient fleet support: a minimum of {war.fleet_support} fleets are required to prosecute this war",
            )

        # Create consent required status if below minimum force
        if war.naval_strength > 0:
            effective_commander_strength = (
                commander.military if naval_force > commander.military else naval_force
            )
            force_strength = effective_commander_strength + naval_force
            minimum_force = war.naval_strength
        else:
            land_force = sum(l.strength for l in legions)
            if existing_campaign:
                land_force += sum(l.strength for l in existing_campaign.legions.all())
            effective_commander_strength = (
                commander.military if land_force > commander.military else land_force
            )
            force_strength = effective_commander_strength + land_force
            minimum_force = war.naval_strength
        if force_strength < minimum_force:
            commander.add_status_item(Senator.StatusItem.CONSENT_REQUIRED)
            commander.save()

        # Determine proposal
        proposal = "Deploy"
        if not commander_already_deployed:
            proposal += f" {commander.display_name}"
            if len(legions) + len(fleets) > 0:
                proposal += " with command of"
        if len(legions) > 0:
            legion_names = unit_list_to_string(list(legions))
            proposal += f" {len(legions)} {'legions' if len(legions) > 1 else 'legion'} ({legion_names})"
            if len(fleets) > 0:
                proposal += " and"
        if len(fleets) > 0:
            fleet_names = unit_list_to_string(list(fleets))
            proposal += f" {len(fleets)} {'fleets' if len(fleets) > 1 else 'fleet'} ({fleet_names})"
        proposal += " to"
        if commander_already_deployed:
            proposal += f" join {commander.display_name}"
            proposal += "'" if commander.display_name.endswith("s") else "'s"
            proposal += " Campaign in"
        proposal += f" the {war.name}"

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
