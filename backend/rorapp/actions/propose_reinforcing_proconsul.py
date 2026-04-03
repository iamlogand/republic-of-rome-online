from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.proposal_available import reinforcing_proconsul_proposal_available
from rorapp.helpers.senate_proposal import faction_can_propose, log_proposal, senate_open_for_proposals
from rorapp.models import (
    AvailableAction,
    Campaign,
    EnemyLeader,
    Faction,
    Fleet,
    Game,
    Legion,
    Senator,
)
from rorapp.helpers.unit_lists import unit_list_to_string


class ProposeReinforcingProconsulAction(ActionBase):
    NAME = "Propose reinforcing proconsul"
    POSITION = 3

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and senate_open_for_proposals(game_state, Game.SubPhase.OTHER_BUSINESS)
            and faction_can_propose(game_state, faction)
            and reinforcing_proconsul_proposal_available(game_state)
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            reinforceable_campaigns = sorted(
                [
                    c
                    for c in snapshot.campaigns
                    if c.commander is not None and not c.recently_deployed
                ],
                key=lambda c: c.id,
            )

            available_legions = sorted(
                [l for l in snapshot.legions if l.campaign_id is None],
                key=lambda l: l.number,
            )
            available_fleets = sorted(
                [f for f in snapshot.fleets if f.campaign_id is None],
                key=lambda f: f.number,
            )

            return [
                AvailableAction.objects.create(
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
                                }
                                for c in reinforceable_campaigns
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
                    ],
                )
            ]
        return []

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)

        # Retrieve and validate campaign
        campaign_id = int(selection["Campaign"])
        campaign = (
            Campaign.objects.select_related("commander", "war")
            .prefetch_related("legions", "fleets")
            .get(game=game, id=campaign_id)
        )

        # Check campaign has a commander
        if campaign.commander is None:
            return ExecutionResult(
                False, "Cannot reinforce a campaign without a commander."
            )

        # Check campaign wasn't recently deployed
        if campaign.recently_deployed:
            return ExecutionResult(
                False,
                "Cannot reinforce a campaign that was deployed this turn.",
            )

        legion_ids = selection["Legions"] if "Legions" in selection else []
        legions = Legion.objects.filter(game=game, id__in=legion_ids).order_by("number")
        if len(legion_ids) != len(legions):
            return ExecutionResult(False, "Invalid legions selected.")

        fleet_ids = selection["Fleets"] if "Fleets" in selection else []
        fleets = Fleet.objects.filter(game=game, id__in=fleet_ids).order_by("number")
        if len(fleet_ids) != len(fleets):
            return ExecutionResult(False, "Invalid fleets selected.")

        if not legions and not fleets:
            return ExecutionResult(False, "No legions or fleets selected.")

        # Check all selected forces are available (not already deployed)
        for legion in legions:
            if legion.campaign_id is not None:
                return ExecutionResult(False, "Selected legion is already deployed.")

        for fleet in fleets:
            if fleet.campaign_id is not None:
                return ExecutionResult(False, "Selected fleet is already deployed.")

        war = campaign.war
        commander = campaign.commander

        # Calculate total force after reinforcement
        land_force = sum(l.strength for l in campaign.legions.all()) + sum(
            l.strength for l in legions
        )
        naval_force = len(campaign.fleets.all()) + len(fleets)

        # Check force requirements for the war
        if war.naval_strength == 0:
            if land_force == 0:
                return ExecutionResult(
                    False, "A minimum of 1 legion is required for the land battle."
                )
            if naval_force < war.fleet_support:
                fleets_text = (
                    str(war.fleet_support)
                    + " fleet"
                    + ("s are" if war.fleet_support > 1 else " is")
                )
                return ExecutionResult(
                    False,
                    f"Insufficient fleet support: at least {fleets_text} required to support the land battle.",
                )
        else:
            if naval_force == 0:
                return ExecutionResult(
                    False, "A minimum of 1 fleet is required for the naval battle."
                )

        # Create consent required status if below minimum force
        leader_strength = sum(
            l.strength
            for l in EnemyLeader.objects.filter(game=game, series_name=war.series_name, active=True)
        )
        if war.naval_strength > 0:
            effective_commander_strength = (
                commander.military if naval_force > commander.military else naval_force
            )
            force_strength = effective_commander_strength + naval_force
            minimum_force = war.naval_strength + leader_strength
        else:
            effective_commander_strength = (
                commander.military if land_force > commander.military else land_force
            )
            force_strength = effective_commander_strength + land_force
            minimum_force = war.land_strength + leader_strength
        if force_strength < minimum_force:
            commander.add_status_item(Senator.StatusItem.CONSENT_REQUIRED)
            commander.save()

        # Determine proposal
        proposal = f"Reinforce {campaign.display_name} with"
        proposal += f" {unit_list_to_string(list(legions), list(fleets))}"
        proposal += f" in the {war.name}"

        # Validate proposal
        if game.has_defeated_proposal(proposal):
            return ExecutionResult(False, "This proposal was previously rejected")

        # Set current proposal
        game.current_proposal = proposal
        game.save()

        log_proposal(game_id, faction, game)

        return ExecutionResult(True)
