from typing import Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
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
)
from rorapp.helpers.unit_lists import unit_list_to_string


class ProposeRecallingForcesAction(ActionBase):
    NAME = "Propose recalling forces"
    POSITION = 2

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
            deployed_legions = [
                l for l in game_state.legions if l.campaign_id is not None
            ]
            deployed_fleets = [
                f for f in game_state.fleets if f.campaign_id is not None
            ]
            campaign__commander_ids = [c.commander_id for c in game_state.campaigns]
            deployed_commanders = [
                s for s in game_state.senators if s in campaign__commander_ids
            ]
            if (
                len(deployed_legions) + len(deployed_fleets) + len(deployed_commanders)
                > 0
            ):
                return faction

        return []

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            deployed_legions = sorted(
                [l for l in snapshot.legions if l.campaign_id is not None],
                key=lambda l: l.number,
            )
            deployed_fleets = sorted(
                [f for f in snapshot.fleets if f.campaign_id is not None],
                key=lambda f: f.number,
            )
            proconsul_ids = [
                s.id for s in snapshot.senators if s.has_title(Senator.Title.PROCONSUL)
            ]
            proconsul_campaigns = [
                c
                for c in snapshot.campaigns
                if c.commander_id is None or c.commander_id in proconsul_ids
            ]

            return [AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Campaign",
                        "options": [
                            {
                                "value": c.id,
                                "object_class": "campaign",
                                "id": c.id,
                                "signals": {
                                    "campaign": c.id,
                                    "commander": c.commander_id,
                                },
                            }
                            for c in proconsul_campaigns
                        ],
                    },
                    {
                        "type": "boolean",
                        "name": "Recall commander",
                        "conditions": [
                            {
                                "value1": "signal:commander",
                                "operation": "!=",
                                "value2": None,
                            },
                        ],
                    },
                    {
                        "type": "multiselect",
                        "name": "Legions",
                        "options": [
                            {
                                "value": l.id,
                                "object_class": "legion",
                                "id": l.id,
                                "conditions": [
                                    {
                                        "value1": "signal:campaign",
                                        "operation": "==",
                                        "value2": l.campaign_id,
                                    },
                                ],
                            }
                            for l in deployed_legions
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
                                "conditions": [
                                    {
                                        "value1": "signal:campaign",
                                        "operation": "==",
                                        "value2": f.campaign_id,
                                    },
                                ],
                            }
                            for f in deployed_fleets
                        ],
                        "inline": True,
                    },
                ],
            )]
        return []

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, str],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)

        campaign_id = int(selection["Campaign"])
        campaign = (
            Campaign.objects.select_related("commander", "war")
            .prefetch_related("legions", "fleets")
            .get(game=game, id=campaign_id)
        )

        legion_ids = selection["Legions"] if "Legions" in selection else []
        legions = Legion.objects.filter(game=game, id__in=legion_ids).order_by("number")
        if len(legion_ids) != len(legions):
            return ExecutionResult(False, "Invalid legions selected.")

        fleet_ids = selection["Fleets"] if "Fleets" in selection else []
        fleets = Fleet.objects.filter(game=game, id__in=fleet_ids).order_by("number")
        if len(fleet_ids) != len(fleets):
            return ExecutionResult(False, "Invalid fleets selected.")

        # Check that all forces are in the same campaign
        mismatch = False
        for legion in legions:
            if legion.campaign_id != campaign_id:
                mismatch = True
        for fleet in fleets:
            if fleet.campaign_id != campaign_id:
                mismatch = True
        if mismatch:
            return ExecutionResult(
                False, "All recalled forces must be from the same campaign."
            )

        # Check that force hasn't recently been deployed or reinforced
        if campaign.recently_deployed or campaign.recently_reinforced:
            return ExecutionResult(
                False,
                "Forces that were deployed or reinforced this turn can't be recalled.",
            )

        # Check that something is being recalled
        if len(legions) + len(fleets) == 0:
            return ExecutionResult(False, "No legions or fleets selected.")

        # Check that all forces are recalled if the commander is being recalled
        recall_commander = (
            selection["Recall commander"] if "Recall commander" in selection else False
        )
        if recall_commander and (
            len(legions) < len(campaign.legions.all())
            or len(fleets) < len(campaign.fleets.all())
        ):
            return ExecutionResult(
                False,
                "If the commander is recalled, all his forces must be recalled as well.",
            )

        commander = campaign.commander
        war = campaign.war
        land_force = sum(l.strength for l in campaign.legions.all()) - sum(
            l.strength for l in legions
        )
        naval_force = len(campaign.fleets.all()) - len(fleets)

        # Check remaining force won't be automatically recalled when senate closes
        if war.naval_strength == 0:
            if (
                (commander and not recall_commander) or naval_force > 0
            ) and land_force == 0:
                return ExecutionResult(
                    False,
                    "A minimum of 1 legion must remain for the land battle. Leave at least 1 legion or recall all forces.",
                )
            if (
                (commander and not recall_commander) or land_force > 0
            ) and naval_force < war.fleet_support:
                fleet_text = (
                    str(war.fleet_support)
                    + " fleet"
                    + ("s" if war.fleet_support > 1 else "")
                )
                return ExecutionResult(
                    False,
                    f"Insufficient fleet support: a minimum of {fleet_text} must remain to support the land battle.",
                )
        else:
            if (
                commander and not recall_commander and land_force > 0
            ) and naval_force == 0:
                return ExecutionResult(
                    False,
                    "A minimum of 1 fleet must remain for the naval battle. Leave at least 1 fleet or recall all forces.",
                )

        # Create consent required status if below minimum force
        if commander and not recall_commander:
            if war.naval_strength > 0:
                effective_commander_strength = (
                    commander.military
                    if naval_force > commander.military
                    else naval_force
                )
                force_strength = effective_commander_strength + naval_force
                minimum_force = war.naval_strength
            else:
                effective_commander_strength = (
                    commander.military
                    if land_force > commander.military
                    else land_force
                )
                force_strength = effective_commander_strength + land_force
                minimum_force = war.naval_strength
            if force_strength < minimum_force:
                commander.add_status_item(Senator.StatusItem.CONSENT_REQUIRED)
                commander.save()

        # Determine proposal
        proposal = "Recall"
        if commander and recall_commander:
            proposal += f" {commander.display_name}"
            if len(legions) > 0 and len(fleets) > 0:
                proposal += ","
            else:
                proposal += " and"
        if len(legions) + len(fleets) > 0:
            proposal += f" {unit_list_to_string(list(legions), list(fleets))}"
        proposal += " from"
        if not campaign.commander:
            proposal += " the"
        proposal += f" {campaign.display_name} in the {war.name}"

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
