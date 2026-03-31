from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.proposal_available import raising_forces_proposal_available
from rorapp.helpers.senate_proposal import faction_can_propose, log_proposal, senate_open_for_proposals
from rorapp.helpers.text import pluralize
from rorapp.models import AvailableAction, Faction, Game, Legion


class ProposeRaisingForcesAction(ActionBase):
    NAME = "Propose raising forces"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and senate_open_for_proposals(game_state, Game.SubPhase.OTHER_BUSINESS)
            and faction_can_propose(game_state, faction)
            and raising_forces_proposal_available(game_state)
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            state_treasury = snapshot.game.state_treasury
            max_recruitment = state_treasury // 10
            max_new_legions = 25 - len(snapshot.legions)
            max_new_fleets = 25 - len(snapshot.fleets)

            return [AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "number",
                        "name": "Legions",
                        "min": [0],
                        "max": [
                            max_recruitment,
                            max_new_legions,
                            f"{max_recruitment} - signal:fleets",
                        ],
                        "signals": {
                            "legions": "VALUE",
                        },
                    },
                    {
                        "type": "number",
                        "name": "Fleets",
                        "min": [0],
                        "max": [
                            max_recruitment,
                            max_new_fleets,
                            f"{max_recruitment} - signal:legions",
                        ],
                        "signals": {
                            "fleets": "VALUE",
                        },
                    },
                ],
            )]
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

        new_legions = int(selection["Legions"])
        new_fleets = int(selection["Fleets"])

        # Validate total cost
        recruitment_cost = (new_legions + new_fleets) * 10
        if recruitment_cost > game.state_treasury:
            return ExecutionResult(
                False, "The State cannot afford to recruit this many forces"
            )

        # Determine proposal
        if new_legions > 0:
            if new_fleets > 0:
                proposal = f"Raise {pluralize(new_legions, 'legion')} and {pluralize(new_fleets, 'fleet')}"
            else:
                proposal = f"Raise {pluralize(new_legions, 'legion')}"
        else:
            if new_fleets > 0:
                proposal = f"Raise {pluralize(new_fleets, 'fleet')}"
            else:
                return ExecutionResult(
                    False, "Proposal must include at least 1 legion or fleet"
                )

        # Validate proposal
        if proposal in game.defeated_proposals:
            return ExecutionResult(False, "This proposal was previously rejected.")

        # Set current proposal
        game.current_proposal = proposal
        game.save()

        log_proposal(game_id, faction, game)

        return ExecutionResult(True)
