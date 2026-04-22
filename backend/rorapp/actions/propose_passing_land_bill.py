from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.proposal_available import (
    land_bill_proposal_available,
    LAND_BILL_TYPES,
)
from rorapp.helpers.text import format_list
from rorapp.helpers.senate_proposal import (
    faction_can_propose,
    log_proposal,
    senate_open_for_proposals,
)
from rorapp.models import AvailableAction, Faction, Game, Senator


class ProposePassingLandBillAction(ActionBase):
    NAME = "Propose passing land bill"
    POSITION = 6

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and senate_open_for_proposals(game_state, Game.SubPhase.OTHER_BUSINESS)
            and faction_can_propose(game_state, faction)
            and land_bill_proposal_available(game_state)
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
        available_types = [
            bill_type
            for bill_type, effect, max_count in LAND_BILL_TYPES
            if not game.has_unavailable_proposal(f"pass type {bill_type} land bill")
            and game.count_effect(effect) < max_count
        ]

        senators_in_rome = sorted(
            [
                s
                for s in snapshot.senators
                if s.faction and s.alive and s.location == "Rome"
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
                            {"value": t, "name": f"type {t}"} for t in available_types
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
                    {
                        "type": "select",
                        "name": "Co-sponsor",
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
        if bill_type not in ("I", "II", "III"):
            return ExecutionResult(False, "Invalid bill type.")

        if game.has_unavailable_proposal(f"pass type {bill_type} land bill"):
            return ExecutionResult(
                False,
                f"A type {bill_type} land bill has already been proposed this turn.",
            )

        _, effect, max_count = next(t for t in LAND_BILL_TYPES if t[0] == bill_type)
        if game.count_effect(effect) >= max_count:
            return ExecutionResult(
                False,
                f"The maximum number of type {bill_type} land bills is already in effect.",
            )

        sponsor = Senator.objects.get(game=game_id, id=selection["Sponsor"], alive=True)
        cosponsor = Senator.objects.get(
            game=game_id, id=selection["Co-sponsor"], alive=True
        )

        if sponsor.id == cosponsor.id:
            return ExecutionResult(
                False, "Sponsor and co-sponsor must be different senators."
            )

        proposal = (
            f"Pass type {bill_type} land bill"
            f" sponsored by {sponsor.display_name}"
            f" and co-sponsored by {cosponsor.display_name}"
        )

        game.current_proposal = proposal
        game.save()

        sponsor.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
        sponsor.save()
        cosponsor.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
        cosponsor.save()

        consent_needed = []
        for senator in (sponsor, cosponsor):
            if senator.faction_id != faction.id:
                senator.add_status_item(Senator.StatusItem.CONSENT_REQUIRED)
                senator.save()
                consent_needed.append(senator)

        consent_note = ""
        if consent_needed:
            names = format_list([s.display_name for s in consent_needed])
            consent_note = f" {names} must consent to sponsor the land bill."
        log_proposal(game_id, faction, game, note=consent_note)

        return ExecutionResult(True)
