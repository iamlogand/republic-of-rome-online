from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.governor_candidates import (
    get_eligible_governor_candidates,
    holds_major_office,
    recallable_provinces,
    vacant_forum_provinces,
)
from rorapp.helpers.governor_election import (
    format_grouped_governor_proposal,
    format_governor_proposal,
    governor_field_name,
    is_defeated_governor_pairing,
    is_exclusive_last_remaining_candidate,
    needs_governor_election_vote,
    remaining_candidates_for_province,
    requires_consent,
)
from rorapp.helpers.proposal_available import governor_election_proposal_available
from rorapp.helpers.senate_proposal import log_proposal, senate_open_for_proposals
from rorapp.helpers.text import format_list
from rorapp.models import AvailableAction, Faction, Game, Province, Senator


class NominateGovernorAction(ActionBase):
    NAME = "Nominate governor"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
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
                    if s.faction
                    and s.faction.id == faction.id
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

    def _eligible_provinces(
        self,
        vacant_provinces: List[Province],
        recallable: List[Province],
        candidate_senators: List[Senator],
        defeated_proposals: list[str],
    ) -> List[Province]:
        return [
            province
            for province in vacant_provinces
            if needs_governor_election_vote(
                province, vacant_provinces, candidate_senators, defeated_proposals
            )
        ] + [
            province
            for province in recallable
            if remaining_candidates_for_province(
                province, candidate_senators, defeated_proposals
            )
        ]

    def _governor_options(
        self,
        province: Province,
        candidate_senators: List[Senator],
        defeated_proposals: list[str],
        *,
        use_province_signal: bool,
    ) -> List[dict]:
        options = []
        for senator in candidate_senators:
            if is_defeated_governor_pairing(
                province.name, senator, defeated_proposals
            ):
                continue
            if senator.faction_id is None and requires_consent(
                senator, province, candidate_senators, defeated_proposals
            ):
                continue
            option = {
                "value": senator.id,
                "object_class": "senator",
                "id": senator.id,
            }
            if use_province_signal:
                option["conditions"] = [
                    {
                        "value1": "signal:province_id",
                        "operation": "==",
                        "value2": province.id,
                    },
                ]
            options.append(option)
        return options

    def get_schema(
        self, game_state_snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(game_state_snapshot, faction_id)
        if not faction:
            return []

        defeated_proposals = list(game_state_snapshot.game.defeated_proposals)
        vacant_provinces = vacant_forum_provinces(game_state_snapshot.game.id)
        candidate_senators = get_eligible_governor_candidates(
            game_state_snapshot.senators
        )
        eligible_provinces = self._eligible_provinces(
            vacant_provinces,
            recallable_provinces(game_state_snapshot.game.id),
            candidate_senators,
            defeated_proposals,
        )

        if not eligible_provinces:
            return []

        if len(eligible_provinces) == 1:
            province = eligible_provinces[0]
            governor_options = self._governor_options(
                province,
                candidate_senators,
                defeated_proposals,
                use_province_signal=True,
            )
            if not governor_options:
                return []
            return [
                AvailableAction.objects.create(
                    game=game_state_snapshot.game,
                    faction=faction,
                    base_name=self.NAME,
                    position=self.POSITION,
                    field_descriptors=[
                        {
                            "type": "select",
                            "name": "Province",
                            "options": [
                                {
                                    "value": province.id,
                                    "object_class": "province",
                                    "id": province.id,
                                    "signals": {
                                        "province_id": province.id,
                                    },
                                }
                            ],
                        },
                        {
                            "type": "select",
                            "name": "Governor",
                            "group_by": "faction",
                            "options": governor_options,
                        },
                    ],
                )
            ]

        province_options = [
            {
                "value": province.id,
                "object_class": "province",
                "id": province.id,
                "signals": {f"province_{province.id}": 1},
            }
            for province in eligible_provinces
        ]
        field_descriptors: List[dict] = [
            {
                "type": "multiselect",
                "name": "Provinces",
                "options": province_options,
            },
        ]
        for province in eligible_provinces:
            governor_options = self._governor_options(
                province,
                candidate_senators,
                defeated_proposals,
                use_province_signal=False,
            )
            if not governor_options:
                continue
            field_descriptors.append(
                {
                    "type": "select",
                    "name": governor_field_name(province.name),
                    "group_by": "faction",
                    "options": governor_options,
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
                game=game_state_snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=field_descriptors,
            )
        ]

    def _validate_pairing(
        self,
        game: Game,
        province: Province,
        senator: Senator,
        candidate_senators: List[Senator],
        vacant_provinces: List[Province],
    ) -> Optional[str]:
        if senator.location != "Rome":
            return f"{senator.display_name} is not in Rome."
        if holds_major_office(senator):
            return f"{senator.display_name} holds a major office and is ineligible."
        if is_defeated_governor_pairing(
            province.name, senator, game.defeated_proposals
        ):
            return "This proposal was previously rejected."
        remaining = remaining_candidates_for_province(
            province, candidate_senators, game.defeated_proposals
        )
        if not remaining or senator.id not in {s.id for s in remaining}:
            return f"{senator.display_name} is not eligible for {province.name}."
        if senator.faction_id is None and requires_consent(
            senator, province, candidate_senators, game.defeated_proposals
        ):
            return f"{senator.display_name} is unaligned and cannot consent to govern again this turn."
        if province.governor_id is None and is_exclusive_last_remaining_candidate(
            province, vacant_provinces, candidate_senators, game.defeated_proposals
        ):
            return "The last remaining eligible candidate is appointed automatically."
        return None

    def _put_on_floor(
        self,
        game: Game,
        faction: Faction,
        pairings: list[tuple[Province, Senator]],
        candidate_senators: List[Senator],
    ) -> None:
        game.current_proposal = format_grouped_governor_proposal(pairings)
        game.save()

        consenting = []
        for province, senator in pairings:
            senator.add_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
            if requires_consent(
                senator, province, candidate_senators, game.defeated_proposals
            ):
                senator.add_status_item(Senator.StatusItem.CONSENT_REQUIRED)
                consenting.append(senator.display_name)
            senator.save()

        note = (
            f" {format_list(consenting)} must consent to govern again this turn."
            if consenting
            else ""
        )
        log_proposal(game.id, faction, game, note=note)

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
        candidate_senators = get_eligible_governor_candidates(senators)
        vacant_provinces = vacant_forum_provinces(game_id)
        open_by_id = {
            province.id: province
            for province in vacant_provinces + recallable_provinces(game_id)
        }

        if "Provinces" in selection:
            try:
                province_ids = [int(pid) for pid in selection["Provinces"]]
            except (TypeError, ValueError):
                return ExecutionResult(False, "Invalid province selection.")

            if not province_ids:
                return ExecutionResult(False, "Select at least one province.")

            pairings: list[tuple[Province, Senator]] = []
            used_senator_ids: set[int] = set()

            for province_id in sorted(set(province_ids)):
                province = open_by_id.get(province_id)
                if province is None:
                    return ExecutionResult(False, "Invalid province selection.")

                try:
                    senator_id = int(selection[governor_field_name(province.name)])
                    senator = next(s for s in senators if s.id == senator_id)
                except (KeyError, TypeError, ValueError, StopIteration):
                    return ExecutionResult(
                        False,
                        f"Select a governor for {province.name}.",
                    )

                if senator_id in used_senator_ids:
                    return ExecutionResult(
                        False,
                        f"{senator.display_name} cannot govern multiple provinces.",
                    )

                error = self._validate_pairing(
                    game,
                    province,
                    senator,
                    candidate_senators,
                    vacant_provinces,
                )
                if error:
                    return ExecutionResult(False, error)

                used_senator_ids.add(senator_id)
                pairings.append((province, senator))

            if game.has_defeated_proposal(format_grouped_governor_proposal(pairings)):
                return ExecutionResult(False, "This proposal was previously rejected.")

            self._put_on_floor(game, faction, pairings, candidate_senators)
            return ExecutionResult(True)

        try:
            province_id = int(selection["Province"])
            senator_id = int(selection["Governor"])
            province = open_by_id[province_id]
            senator = next(s for s in senators if s.id == senator_id)
        except (KeyError, TypeError, ValueError, StopIteration):
            return ExecutionResult(False, "Invalid province or governor selection.")

        error = self._validate_pairing(
            game, province, senator, candidate_senators, vacant_provinces
        )
        if error:
            return ExecutionResult(False, error)

        if game.has_defeated_proposal(format_governor_proposal(province.name, senator)):
            return ExecutionResult(False, "This proposal was previously rejected.")

        self._put_on_floor(game, faction, [(province, senator)], candidate_senators)
        return ExecutionResult(True)
