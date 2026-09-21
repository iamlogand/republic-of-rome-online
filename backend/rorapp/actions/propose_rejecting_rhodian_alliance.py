from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.proposal_available import (
    REJECT_RHODIAN_ALLIANCE_PROPOSAL,
    rhodian_alliance_rejection_proposal_available,
)
from rorapp.helpers.rhodian_alliance import RHODIAN_FLEETS
from rorapp.helpers.senate_proposal import (
    faction_can_propose,
    log_proposal,
    senate_open_for_proposals,
)
from rorapp.models import AvailableAction, Faction, Game


class ProposeRejectingRhodianAllianceAction(ActionBase):
    NAME = "Propose rejecting Rhodian alliance"
    POSITION = 9

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and senate_open_for_proposals(game_state, Game.SubPhase.OTHER_BUSINESS)
            and faction_can_propose(game_state, faction)
            and rhodian_alliance_rejection_proposal_available(game_state)
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        level = snapshot.game.count_effect(GameEffect.RHODIAN_ALLIANCE)
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[],
                context={"fleets": RHODIAN_FLEETS[level]},
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

        game.current_proposal = REJECT_RHODIAN_ALLIANCE_PROPOSAL
        game.save()

        log_proposal(game_id, faction, game)

        return ExecutionResult(True)
