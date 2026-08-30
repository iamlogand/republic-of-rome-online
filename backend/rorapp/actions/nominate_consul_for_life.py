from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.consul_for_life import (
    CONSUL_FOR_LIFE_PREFIX,
    get_eligible_consul_for_life_candidates,
)
from rorapp.helpers.proposal_available import consul_for_life_proposal_available
from rorapp.helpers.senate_proposal import (
    CONSUL_FOR_LIFE_SUB_PHASES,
    faction_can_propose,
    log_proposal,
    senate_open_for_proposals_in,
)
from rorapp.models import AvailableAction, Faction, Game, Senator


class NominateConsulForLifeAction(ActionBase):
    NAME = "Nominate Consul for Life"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and senate_open_for_proposals_in(game_state, CONSUL_FOR_LIFE_SUB_PHASES)
            and faction_can_propose(game_state, faction)
            and consul_for_life_proposal_available(game_state)
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        candidate_senators = sorted(
            get_eligible_consul_for_life_candidates(snapshot.senators),
            key=lambda s: s.family_name,
        )

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {
                        "type": "select",
                        "name": "Consul for Life",
                        "group_by": "faction",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                            }
                            for s in candidate_senators
                        ],
                    }
                ],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        senator = Senator.objects.get(game=game_id, id=selection["Consul for Life"])

        game.current_proposal = f"{CONSUL_FOR_LIFE_PREFIX}{senator.display_name}"
        # Locked at proposal time, so an assassinated nominee cannot be replaced
        # with another nomination this turn (1.09.721)
        game.consul_for_life_proposed = True
        game.save()

        senator.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
        senator.save()

        log_proposal(game_id, faction, game)

        return ExecutionResult(True)
