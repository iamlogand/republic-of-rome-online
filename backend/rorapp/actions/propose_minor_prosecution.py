from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.prosecution_eligibility import (
    get_minor_prosecution_reasons,
    has_minor_prosecution_target,
)
from rorapp.helpers.senate_proposal import can_propose
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class ProposeMinorProsecutionAction(ActionBase):
    NAME = "Propose minor prosecution"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        # Find censor senator
        censor = next(
            (s for s in game_state.senators if s.has_title(Senator.Title.CENSOR)),
            None,
        )
        if not censor:
            return None

        if (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.PROSECUTION
            and (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and can_propose(game_state, faction, allow_tribune=False)
            and game_state.game.prosecutions_remaining >= 1
            and not any(
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
            )
            and has_minor_prosecution_target(
                game_state.senators,
                game_state.game.defeated_proposals,
                censor.id,
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        censor = next(
            (s for s in snapshot.senators if s.has_title(Senator.Title.CENSOR)),
            None,
        )
        if not censor:
            return []

        # Eligible accused: alive, in Rome, not censor, has at least one valid reason
        eligible_accused = []
        for senator in snapshot.senators:
            if (
                senator.alive
                and senator.location == "Rome"
                and senator.id != censor.id
                and get_minor_prosecution_reasons(
                    senator, snapshot.game.defeated_proposals
                )
            ):
                eligible_accused.append(senator)

        # Eligible prosecutors: alive, has faction, not accused (handled via conditions), not censor
        eligible_prosecutors = sorted(
            [
                s
                for s in snapshot.senators
                if s.alive and s.faction and s.id != censor.id
            ],
            key=lambda s: s.family_name,
        )

        eligible_accused = sorted(eligible_accused, key=lambda s: s.family_name)

        # Build reason options per accused (using context)
        accused_options = []
        for senator in eligible_accused:
            available_reasons = get_minor_prosecution_reasons(
                senator, snapshot.game.defeated_proposals
            )
            accused_options.append(
                {
                    "value": senator.id,
                    "object_class": "senator",
                    "id": senator.id,
                    "signals": {
                        "accused_id": senator.id,
                    },
                    "context": {
                        "reasons": available_reasons,
                    },
                }
            )

        # Build per-reason mapping of which accused senator IDs have each reason available
        reason_to_senator_ids: dict[str, set[int]] = {}
        for senator in eligible_accused:
            for r in get_minor_prosecution_reasons(
                senator, snapshot.game.defeated_proposals
            ):
                reason_to_senator_ids.setdefault(r, set()).add(senator.id)

        all_eligible_ids = {s.id for s in eligible_accused}

        # Each reason gets conditions excluding senators who don't have that reason,
        # so only valid reasons appear when a specific accused is selected
        reason_options = [
            {
                "value": reason,
                "name": (
                    reason[len("corruption via ") :]
                    if reason.startswith("corruption via ")
                    else reason
                ),
                "conditions": [
                    {
                        "value1": "signal:accused_id",
                        "operation": "!=",
                        "value2": senator_id,
                    }
                    for senator_id in sorted(
                        all_eligible_ids - reason_to_senator_ids[reason]
                    )
                ],
            }
            for reason in sorted(reason_to_senator_ids.keys())
        ]

        prosecutor_options = [
            {
                "value": s.id,
                "object_class": "senator",
                "id": s.id,
                "conditions": [
                    {
                        "value1": "signal:accused_id",
                        "operation": "!=",
                        "value2": s.id,
                    }
                ],
            }
            for s in eligible_prosecutors
        ]

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Accused",
                        "options": accused_options,
                    },
                    {
                        "type": "select",
                        "name": "Reason",
                        "options": reason_options,
                    },
                    {
                        "type": "select",
                        "name": "Prosecutor",
                        "options": prosecutor_options,
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
        senators = Senator.objects.filter(game=game_id)

        accused_id = selection["Accused"]
        reason_str = selection["Reason"]
        prosecutor_id = selection["Prosecutor"]

        if accused_id == prosecutor_id:
            return ExecutionResult(
                False, "The accused cannot serve as their own prosecutor."
            )

        accused = senators.get(id=accused_id)
        prosecutor = senators.get(id=prosecutor_id)

        valid_reasons = get_minor_prosecution_reasons(accused, game.defeated_proposals)
        if reason_str not in valid_reasons:
            return ExecutionResult(False, "Invalid prosecution reason.")

        game.current_proposal = f"Prosecute {accused.display_name} for {reason_str}"
        # Accused's influence adds to votes nay
        game.votes_nay += accused.influence
        game.save()

        accused.add_status_item(Senator.StatusItem.ACCUSED)
        accused.save()
        prosecutor.add_status_item(Senator.StatusItem.CONSENT_REQUIRED)
        prosecutor.save()

        censor = next(
            (s for s in senators if s.has_title(Senator.Title.CENSOR)),
            None,
        )
        censor_name = censor.display_name if censor else "Censor"
        Log.create_object(
            game_id,
            f"{censor_name} proposed the motion: {game.current_proposal}. {prosecutor.display_name} must consent to serve as prosecutor.",
        )

        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.save()

        return ExecutionResult(True)
