from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.proposal_available import (
    land_bill_repeal_proposal_available,
    LAND_BILL_REPEAL_SPONSOR_POP_REQUIRED,
    LAND_BILL_TYPES,
)
from rorapp.helpers.senate_proposal import (
    faction_can_propose,
    log_proposal,
    senate_open_for_proposals,
)
from rorapp.models import AvailableAction, Faction, Game, Senator

_REPEALABLE_TYPES = [(t, effect) for t, effect, _ in LAND_BILL_TYPES if t != "I"]


class ProposeRepealingLandBillAction(ActionBase):
    NAME = "Propose repealing land bill"
    POSITION = 7

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and senate_open_for_proposals(game_state, Game.SubPhase.OTHER_BUSINESS)
            and faction_can_propose(game_state, faction)
            and land_bill_repeal_proposal_available(game_state)
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        game = snapshot.game
        repealable_types = [
            bill_type
            for bill_type, effect in _REPEALABLE_TYPES
            if game.count_effect(effect) > 0
        ]

        senators_in_rome = sorted(
            [
                s
                for s in snapshot.senators
                if s.faction
                and s.alive
                and s.location == "Rome"
                and any(
                    s.popularity >= LAND_BILL_REPEAL_SPONSOR_POP_REQUIRED[t]
                    for t in repealable_types
                )
            ],
            key=lambda s: s.family_name,
        )

        return [
            AvailableAction.objects.create(
                game=game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Bill type",
                        "options": [
                            {"value": t, "name": f"type {t}"} for t in repealable_types
                        ],
                    },
                    {
                        "type": "select",
                        "name": "Sponsor",
                        "options": [
                            {"value": s.id, "object_class": "senator", "id": s.id}
                            for s in senators_in_rome
                        ],
                    },
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

        bill_type = selection["Bill type"]
        if bill_type not in ("II", "III"):
            return ExecutionResult(
                False, "Only type II or III land bills can be repealed."
            )

        if game.has_unavailable_proposal(f"repeal type {bill_type} land bill"):
            return ExecutionResult(
                False, "Only one land bill repeal may be attempted per turn."
            )

        effect = {t: eff for t, eff, _ in LAND_BILL_TYPES}[bill_type]
        if game.count_effect(effect) == 0:
            return ExecutionResult(
                False, f"No type {bill_type} land bill is currently in effect."
            )

        sponsor = Senator.objects.get(game=game_id, id=selection["Sponsor"], alive=True)

        required_pop = LAND_BILL_REPEAL_SPONSOR_POP_REQUIRED[bill_type]
        if sponsor.popularity < required_pop:
            return ExecutionResult(
                False,
                f"{sponsor.display_name} does not have sufficient popularity to sponsor this repeal.",
            )

        proposal = (
            f"Repeal type {bill_type} land bill sponsored by {sponsor.display_name}"
        )

        game.current_proposal = proposal
        game.save()

        log_proposal(game_id, faction, game)

        return ExecutionResult(True)
