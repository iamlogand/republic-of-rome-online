from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.governor_election import (
    format_governor_proposal,
    governor_candidates,
    governor_field_name,
    is_defeated_governor_pairing,
    nominatable_provinces,
    remaining_candidates,
)
from rorapp.helpers.proposal_available import governor_election_proposal_available
from rorapp.helpers.senate_proposal import log_proposal, senate_open_for_proposals
from rorapp.models import AvailableAction, Faction, Game, Province, Senator


class NominateGovernorAction(ActionBase):
    NAME = "Nominate governor"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        if not settings.FEATURE_FLAGS.get("governors"):
            return None
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and senate_open_for_proposals(
                game_state,
                Game.SubPhase.GOVERNOR_ELECTION,
                Game.SubPhase.OTHER_BUSINESS,
            )
            and governor_election_proposal_available(game_state)
            and not any(
                s.has_status_item(Senator.StatusItem.UNANIMOUSLY_DEFEATED)
                for s in game_state.senators
            )
            and (
                any(
                    s
                    for s in game_state.senators
                    if s.faction_id == faction.id
                    and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
                )
                and not any(
                    f
                    for f in game_state.factions
                    if f.id != faction.id
                    and f.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
                )
                or faction.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
            )
        ):
            return faction
        return None

    def _governor_options(
        self,
        province: Province,
        candidates: List[Senator],
        defeated_proposals: List[str],
    ) -> List[dict]:
        return [
            {"value": senator.id, "object_class": "senator", "id": senator.id}
            for senator in candidates
            if not is_defeated_governor_pairing(
                province.name, senator, defeated_proposals
            )
        ]

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        defeated_proposals = snapshot.game.defeated_proposals
        candidates = governor_candidates(snapshot.senators)
        contested = nominatable_provinces(
            snapshot.provinces, candidates, defeated_proposals
        )
        if not contested:
            return []

        if len(contested) == 1:
            province = contested[0]
            field_descriptors: List[dict] = [
                {
                    "type": "select",
                    "name": "Province",
                    "options": [
                        {
                            "value": province.id,
                            "object_class": "province",
                            "id": province.id,
                        }
                    ],
                },
                {
                    "type": "select",
                    "name": "Governor",
                    "group_by": "faction",
                    "options": self._governor_options(
                        province, candidates, defeated_proposals
                    ),
                },
            ]
        else:
            field_descriptors = [
                {
                    "type": "multiselect",
                    "name": "Provinces",
                    "options": [
                        {
                            "value": province.id,
                            "object_class": "province",
                            "id": province.id,
                            "signals": {f"province_{province.id}": 1},
                        }
                        for province in contested
                    ],
                }
            ]
            # Governorships may be elected in tandem, so each selected province
            # reveals its own list of candidates (1.09.5)
            for province in contested:
                field_descriptors.append(
                    {
                        "type": "select",
                        "name": governor_field_name(province.name),
                        "group_by": "faction",
                        "options": self._governor_options(
                            province, candidates, defeated_proposals
                        ),
                        "conditions": [
                            {
                                "value1": f"signal:province_{province.id}",
                                "operation": "==",
                                "value2": 1,
                            }
                        ],
                    }
                )

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=field_descriptors,
            )
        ]

    def _pairing_error(
        self,
        province: Province,
        senator: Senator,
        nominatable: List[Province],
        candidates: List[Senator],
        defeated_proposals: List[str],
    ) -> Optional[str]:
        if province.id not in {p.id for p in nominatable}:
            return f"{province.name} is not open to a vote."
        eligible = remaining_candidates(province, candidates, defeated_proposals)
        if senator.id not in {s.id for s in eligible}:
            return f"{senator.display_name} is not eligible for {province.name}."
        return None

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        senators = list(Senator.objects.filter(game_id=game_id, alive=True))
        candidates = governor_candidates(senators)
        nominatable = nominatable_provinces(
            list(Province.objects.filter(game_id=game_id)),
            candidates,
            game.defeated_proposals,
        )
        nominatable_by_id = {province.id: province for province in nominatable}

        single = "Province" in selection
        if single:
            province_ids = [selection["Province"]]
        elif "Provinces" in selection:
            province_ids = list(selection["Provinces"])
        else:
            return ExecutionResult(False, "Select at least one province.")

        pairings: List[Tuple[Province, Senator]] = []
        for province_id in province_ids:
            try:
                province = nominatable_by_id[int(province_id)]
            except (KeyError, TypeError, ValueError):
                return ExecutionResult(False, "Invalid province selection.")

            field = "Governor" if single else governor_field_name(province.name)
            senator = next(
                (s for s in senators if str(s.id) == str(selection.get(field))), None
            )
            if senator is None:
                return ExecutionResult(False, f"Select a governor for {province.name}.")
            if any(senator.id == paired.id for _, paired in pairings):
                return ExecutionResult(
                    False, f"{senator.display_name} cannot govern two provinces."
                )

            error = self._pairing_error(
                province, senator, nominatable, candidates, game.defeated_proposals
            )
            if error:
                return ExecutionResult(False, error)
            pairings.append((province, senator))

        if not pairings:
            return ExecutionResult(False, "Select at least one province.")

        proposal = format_governor_proposal(pairings)
        if game.has_defeated_proposal(proposal):
            return ExecutionResult(False, "This proposal was previously rejected.")

        game.current_proposal = proposal
        game.save()
        for _, senator in pairings:
            senator.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
            senator.save()
        log_proposal(game.id, faction, game)
        return ExecutionResult(True)
