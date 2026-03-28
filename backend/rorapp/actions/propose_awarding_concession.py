from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.concession import Concession
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.senate_proposal import can_propose, log_proposal
from rorapp.models import AvailableAction, Faction, Game, Senator


class ProposeAwardingConcessionAction(ActionBase):
    NAME = "Propose awarding concession"
    POSITION = 0

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
            and can_propose(game_state, faction)
            and len(game_state.game.concessions) > 0
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            senators = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction and s.alive
                ],
                key=lambda s: s.family_name,
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
                            "name": "Concession",
                            "options": [
                                {
                                    "value": c,
                                    "name": c,
                                }
                                for c in snapshot.game.concessions
                            ],
                        },
                        {
                            "type": "select",
                            "name": "Senator",
                            "options": [
                                {
                                    "value": s.id,
                                    "object_class": "senator",
                                    "id": s.id,
                                }
                                for s in senators
                            ],
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

        # Parse concession
        concession_value = selection["Concession"]
        try:
            concession = Concession(concession_value)
        except ValueError:
            return ExecutionResult(False, "Invalid concession.")

        if concession_value not in game.concessions:
            return ExecutionResult(False, "Concession is not available.")

        # Get senator
        senator = Senator.objects.get(
            game=game_id, id=selection["Senator"], alive=True
        )

        # Build proposal
        proposal = f"Award the {concession.value} concession to {senator.display_name}"

        # Validate proposal
        if proposal in game.defeated_proposals:
            return ExecutionResult(False, "This proposal was previously rejected.")

        # Set current proposal
        game.current_proposal = proposal
        game.save()

        log_proposal(game_id, faction, game)

        return ExecutionResult(True)
