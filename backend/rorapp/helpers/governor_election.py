from rorapp.helpers.governor_candidates import (
    get_eligible_governor_candidates,
    recallable_provinces,
    vacant_forum_provinces,
)
from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.transfer_presiding_magistrate import (
    transfer_presiding_magistrate_to_hrao,
)
from rorapp.models import Game, Province, Senator

PROPOSAL_PREFIX = "Elect governor of "
PROPOSAL_PREFIX_PLURAL = "Elect governors of "
PAIR_SEPARATOR = " and "


def format_governor_pair(province_name: str, senator: Senator) -> str:
    return f"{province_name}: {senator.display_name}"


def format_governor_proposal(province_name: str, senator: Senator) -> str:
    return f"{PROPOSAL_PREFIX}{format_governor_pair(province_name, senator)}"


def format_grouped_governor_proposal(
    pairings: list[tuple[Province, Senator]],
) -> str:
    sorted_pairings = sorted(pairings, key=lambda pair: pair[0].name)
    body = PAIR_SEPARATOR.join(
        format_governor_pair(province.name, senator)
        for province, senator in sorted_pairings
    )
    if len(sorted_pairings) == 1:
        return f"{PROPOSAL_PREFIX}{body}"
    return f"{PROPOSAL_PREFIX_PLURAL}{body}"


def is_governor_proposal(proposal: str) -> bool:
    return proposal.startswith(PROPOSAL_PREFIX) or proposal.startswith(
        PROPOSAL_PREFIX_PLURAL
    )


def parse_governor_proposals(proposal: str) -> list[tuple[str, str]] | None:
    if proposal.startswith(PROPOSAL_PREFIX_PLURAL):
        body = proposal[len(PROPOSAL_PREFIX_PLURAL) :]
    elif proposal.startswith(PROPOSAL_PREFIX):
        body = proposal[len(PROPOSAL_PREFIX) :]
    else:
        return None

    pairings = []
    for part in body.split(PAIR_SEPARATOR):
        if ": " not in part:
            return None
        province_name, senator_name = part.rsplit(": ", 1)
        if not province_name or not senator_name:
            return None
        pairings.append((province_name, senator_name))
    return pairings


def defeated_governor_pairings(defeated_proposals: list[str]) -> set[str]:
    # A defeated joint motion does not rule out its pairings on their own (1.09.131)
    defeated: set[str] = set()
    for proposal in defeated_proposals:
        if proposal.startswith(PROPOSAL_PREFIX_PLURAL):
            continue
        if proposal.startswith(PROPOSAL_PREFIX):
            defeated.add(proposal[len(PROPOSAL_PREFIX) :])
    return defeated


def is_defeated_governor_pairing(
    province_name: str, senator: Senator, defeated_proposals: list[str]
) -> bool:
    pair = format_governor_pair(province_name, senator)
    return pair in defeated_governor_pairings(defeated_proposals)


def governor_election_inputs(
    game_id: int,
    senators=None,
    defeated_proposals: list[str] | None = None,
) -> tuple[list[Province], list[Senator], list[str]]:
    vacant = vacant_forum_provinces(game_id)
    if senators is None:
        senators = list(Senator.objects.filter(game_id=game_id, alive=True))
    if defeated_proposals is None:
        defeated_proposals = list(
            Game.objects.only("defeated_proposals").get(id=game_id).defeated_proposals
        )
    candidates = get_eligible_governor_candidates(senators)
    return vacant, candidates, defeated_proposals


def remaining_candidates_for_province(
    province: Province,
    candidates: list[Senator],
    defeated_proposals: list[str],
) -> list[Senator]:
    return [
        senator
        for senator in candidates
        if not is_defeated_governor_pairing(
            province.name, senator, defeated_proposals
        )
    ]


def requires_consent(
    senator: Senator,
    province: Province,
    candidates: list[Senator],
    defeated_proposals: list[str],
) -> bool:
    # A governor who returned or was recalled this turn may not be sent out again
    # without his consent, unless no other candidate remains (1.09.51)
    return senator.has_status_item(Senator.StatusItem.RETURNED_GOVERNOR) and any(
        not candidate.has_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
        for candidate in remaining_candidates_for_province(
            province, candidates, defeated_proposals
        )
    )


def is_exclusive_last_remaining_candidate(
    province: Province,
    vacant: list[Province],
    candidates: list[Senator],
    defeated_proposals: list[str],
) -> bool:
    remaining = remaining_candidates_for_province(
        province, candidates, defeated_proposals
    )
    if len(remaining) != 1:
        return False
    sole = remaining[0]
    # The last candidate for two vacant provinces still needs a vote to decide
    # which one he takes (1.09.54)
    for other in vacant:
        if other.id == province.id:
            continue
        other_remaining = remaining_candidates_for_province(
            other, candidates, defeated_proposals
        )
        if len(other_remaining) == 1 and other_remaining[0].id == sole.id:
            return False
    return True


def needs_governor_election_vote(
    province: Province,
    vacant: list[Province],
    candidates: list[Senator],
    defeated_proposals: list[str],
) -> bool:
    remaining = remaining_candidates_for_province(
        province, candidates, defeated_proposals
    )
    if len(remaining) >= 2:
        return True
    if len(remaining) == 1:
        return not is_exclusive_last_remaining_candidate(
            province, vacant, candidates, defeated_proposals
        )
    return False


def has_governor_election_work_remaining(
    game_id: int,
    senators=None,
    defeated_proposals: list[str] | None = None,
) -> bool:
    vacant, candidates, defeated_proposals = governor_election_inputs(
        game_id, senators, defeated_proposals
    )
    if not vacant or not candidates:
        return False
    return any(
        remaining_candidates_for_province(province, candidates, defeated_proposals)
        for province in vacant
    )


def has_contested_governor_election(
    game_id: int,
    senators=None,
    defeated_proposals: list[str] | None = None,
) -> bool:
    vacant, candidates, defeated_proposals = governor_election_inputs(
        game_id, senators, defeated_proposals
    )
    return any(
        needs_governor_election_vote(
            province, vacant, candidates, defeated_proposals
        )
        for province in vacant
    )


def has_recall_available(
    game_id: int,
    senators=None,
    defeated_proposals: list[str] | None = None,
) -> bool:
    _, candidates, defeated_proposals = governor_election_inputs(
        game_id, senators, defeated_proposals
    )
    return any(
        remaining_candidates_for_province(province, candidates, defeated_proposals)
        for province in recallable_provinces(game_id)
    )


def governor_field_name(province_name: str) -> str:
    return f"Governor for {province_name}"


def next_senate_sub_phase(game_id: int) -> str:
    if has_governor_election_work_remaining(game_id):
        return Game.SubPhase.GOVERNOR_ELECTION
    return Game.SubPhase.OTHER_BUSINESS


def assign_governor(province: Province, senator: Senator) -> None:
    was_hrao = senator.has_title(Senator.Title.HRAO)
    was_presiding_magistrate = senator.has_title(
        Senator.Title.PRESIDING_MAGISTRATE
    )

    province.governor = senator
    province.term = 3
    province.elected_this_turn = True
    province.save()

    senator.location = province.name
    senator.remove_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    senator.remove_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
    if was_hrao:
        senator.remove_title(Senator.Title.HRAO)
    if was_presiding_magistrate:
        senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
    senator.save()

    if was_hrao:
        set_hrao(province.game_id)
    if was_presiding_magistrate:
        transfer_presiding_magistrate_to_hrao(province.game_id)


def return_governor(province: Province, governor: Senator) -> None:
    clear_governorship(province)
    governor.location = "Rome"
    governor.add_status_item(Senator.StatusItem.RETURNED_GOVERNOR)
    governor.save()


def clear_governorship(province: Province) -> None:
    province.governor = None
    province.term = None
    province.elected_this_turn = False
    province.save()
