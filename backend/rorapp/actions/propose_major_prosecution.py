from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.prosecution_eligible import has_major_prosecution_target
from rorapp.helpers.senate_proposal import (
    faction_can_propose,
    senate_open_for_proposals,
)
from rorapp.helpers.text import pluralize, possessive
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class ProposeMajorProsecutionAction(ActionBase):
    NAME = "Propose major prosecution"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        censor = next(
            (s for s in game_state.senators if s.has_title(Senator.Title.CENSOR)),
            None,
        )
        if not censor:
            return None

        if (
            senate_open_for_proposals(game_state, Game.SubPhase.PROSECUTION)
            and faction_can_propose(game_state, faction, allow_tribune=False)
            and game_state.game.prosecutions_remaining == 2
            and not any(
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.CALLED_TO_VOTE)
            )
            and has_major_prosecution_target(
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

        eligible_accused = sorted(
            [
                s
                for s in snapshot.senators
                if s.alive
                and s.location == "Rome"
                and s.id != censor.id
                and s.has_status_item(Senator.StatusItem.MAJOR_CORRUPT)
                and not snapshot.game.has_defeated_proposal(
                    f"Prosecute {s.display_name} for major corruption in office"
                )
            ],
            key=lambda s: s.family_name,
        )

        eligible_prosecutors = sorted(
            [
                s
                for s in snapshot.senators
                if s.alive and s.faction and s.id != censor.id
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
                        "name": "Accused",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                                "signals": {"accused_id": s.id},
                            }
                            for s in eligible_accused
                        ],
                    },
                    {
                        "type": "select",
                        "name": "Prosecutor",
                        "options": [
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
        senators = Senator.objects.filter(game=game_id)

        accused_id = selection["Accused"]
        prosecutor_id = selection["Prosecutor"]

        if accused_id == prosecutor_id:
            return ExecutionResult(
                False, "The accused cannot serve as their own prosecutor."
            )

        accused = senators.get(id=accused_id)
        prosecutor = senators.get(id=prosecutor_id)

        reason = "major corruption in office"
        game.current_proposal = f"Prosecute {accused.display_name} for {reason}"
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
        if accused.influence > 0:
            Log.create_object(
                game_id,
                f"{possessive(accused.display_name)} influence adds {pluralize(accused.influence, 'vote')} against the conviction.",
            )

        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.save()

        return ExecutionResult(True)
