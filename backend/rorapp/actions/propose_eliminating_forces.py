from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.proposal_available import eliminating_forces_proposal_available
from rorapp.helpers.senate_proposal import (
    faction_can_propose,
    log_proposal,
    senate_open_for_proposals,
)
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Faction, Fleet, Game, Legion


class ProposeEliminatingForcesAction(ActionBase):
    NAME = "Propose eliminating forces"
    POSITION = 2

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and senate_open_for_proposals(game_state, Game.SubPhase.OTHER_BUSINESS)
            and faction_can_propose(game_state, faction)
            and eliminating_forces_proposal_available(game_state)
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            eliminable_legions = sorted(
                [
                    l
                    for l in snapshot.legions
                    if l.campaign_id is None and not l.recently_raised
                ],
                key=lambda l: l.number,
            )
            eliminable_fleets = sorted(
                [
                    f
                    for f in snapshot.fleets
                    if f.campaign_id is None and not f.recently_raised
                ],
                key=lambda f: f.number,
            )

            return [
                AvailableAction.objects.create(
                    game=snapshot.game,
                    faction=faction,
                    base_name=self.NAME,
                    position=self.POSITION,
                    field_descriptors=[
                        {
                            "type": "multiselect",
                            "name": "Legions",
                            "options": [
                                {
                                    "value": l.id,
                                    "object_class": "legion",
                                    "id": l.id,
                                }
                                for l in eliminable_legions
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
                                for f in eliminable_fleets
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

        legion_ids = selection["Legions"] if "Legions" in selection else []
        legions = Legion.objects.filter(game=game, id__in=legion_ids).order_by("number")
        if len(legion_ids) != len(legions):
            return ExecutionResult(False, "Invalid legions selected.")

        fleet_ids = selection["Fleets"] if "Fleets" in selection else []
        fleets = Fleet.objects.filter(game=game, id__in=fleet_ids).order_by("number")
        if len(fleet_ids) != len(fleets):
            return ExecutionResult(False, "Invalid fleets selected.")

        # Check that something is being eliminated
        if not legions and not fleets:
            return ExecutionResult(False, "No legions or fleets selected.")

        # Check that all forces are in the reserve (1.09.63)
        if any(l.campaign_id is not None for l in legions) or any(
            f.campaign_id is not None for f in fleets
        ):
            return ExecutionResult(
                False, "Only forces in the reserve can be eliminated."
            )

        # Check that no force was raised this senate phase (1.09.63)
        if any(l.recently_raised for l in legions) or any(
            f.recently_raised for f in fleets
        ):
            return ExecutionResult(
                False,
                "Forces that were raised this senate phase can't be eliminated.",
            )

        # Determine proposal
        proposal = f"Eliminate {unit_list_to_string(list(legions), list(fleets))}"

        # Validate proposal
        if game.has_defeated_proposal(proposal):
            return ExecutionResult(False, "This proposal was previously rejected.")

        # Set current proposal
        game.current_proposal = proposal
        game.save()

        log_proposal(game_id, faction, game)

        return ExecutionResult(True)
