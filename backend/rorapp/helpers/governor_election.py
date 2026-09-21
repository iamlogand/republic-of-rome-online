from typing import List, Optional, Sequence, Tuple

from rorapp.helpers.hrao import MAJOR_OFFICES
from rorapp.models import Province, Senator

PROPOSAL_PREFIX = "Elect governor of "
PROPOSAL_PREFIX_PLURAL = "Elect governors of "
PAIR_SEPARATOR = " and "


def format_governor_proposal(pairings: Sequence[Tuple[Province, Senator]]) -> str:
    ordered = sorted(pairings, key=lambda pair: pair[0].name)
    body = PAIR_SEPARATOR.join(
        format_governor_pair(province.name, senator) for province, senator in ordered
    )
    prefix = PROPOSAL_PREFIX if len(ordered) == 1 else PROPOSAL_PREFIX_PLURAL
    return f"{prefix}{body}"


def format_governor_pair(province_name: str, senator: Senator) -> str:
    return f"{province_name}: {senator.display_name}"


def is_governor_proposal(proposal: str) -> bool:
    return proposal.startswith(PROPOSAL_PREFIX) or proposal.startswith(
        PROPOSAL_PREFIX_PLURAL
    )


def parse_governor_proposal(proposal: str) -> Optional[List[Tuple[str, str]]]:
    if proposal.startswith(PROPOSAL_PREFIX_PLURAL):
        body = proposal[len(PROPOSAL_PREFIX_PLURAL) :]
    elif proposal.startswith(PROPOSAL_PREFIX):
        body = proposal[len(PROPOSAL_PREFIX) :]
    else:
        return None

    pairings = []
    for part in body.split(PAIR_SEPARATOR):
        province_name, separator, senator_name = part.rpartition(": ")
        if not separator or not province_name or not senator_name:
            return None
        pairings.append((province_name, senator_name))
    return pairings


def is_defeated_governor_pairing(
    province_name: str, senator: Senator, defeated_proposals: List[str]
) -> bool:
    # A defeated joint motion does not rule out its pairings on their own (1.09.131)
    pair = format_governor_pair(province_name, senator)
    return f"{PROPOSAL_PREFIX}{pair}" in defeated_proposals


def holds_major_office(senator: Senator) -> bool:
    return any(senator.has_title(title) for title in MAJOR_OFFICES)


def governor_candidates(senators: Sequence[Senator]) -> List[Senator]:
    # The Senate fills a governorship from its membership in Rome, and the holder
    # of a Major Office may not be proposed as a Governor (1.09.5)
    return sorted(
        [
            senator
            for senator in senators
            if senator.alive
            and senator.location == "Rome"
            and not holds_major_office(senator)
            and not senator.has_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
        ],
        key=lambda senator: senator.family_name,
    )


def vacant_provinces(provinces: Sequence[Province]) -> List[Province]:
    return sorted(
        [province for province in provinces if province.governor_id is None],
        key=lambda province: province.name,
    )


def remaining_candidates(
    province: Province,
    candidates: Sequence[Senator],
    defeated_proposals: List[str],
) -> List[Senator]:
    return [
        senator
        for senator in candidates
        if not is_defeated_governor_pairing(province.name, senator, defeated_proposals)
    ]


def open_governorships(
    provinces: Sequence[Province],
    candidates: Sequence[Senator],
    defeated_proposals: List[str],
) -> List[Province]:
    return [
        province
        for province in vacant_provinces(provinces)
        if remaining_candidates(province, candidates, defeated_proposals)
    ]


def is_sole_candidate(
    province: Province,
    vacant: Sequence[Province],
    candidates: Sequence[Senator],
    defeated_proposals: List[str],
) -> bool:
    remaining = remaining_candidates(province, candidates, defeated_proposals)
    if len(remaining) != 1:
        return False
    sole = remaining[0]
    # The last candidate for two vacant provinces still needs a vote to decide
    # which one he takes (1.09.5)
    for other in vacant:
        if other.id == province.id:
            continue
        other_remaining = remaining_candidates(other, candidates, defeated_proposals)
        if len(other_remaining) == 1 and other_remaining[0].id == sole.id:
            return False
    return True


def needs_election_vote(
    province: Province,
    vacant: Sequence[Province],
    candidates: Sequence[Senator],
    defeated_proposals: List[str],
) -> bool:
    # Elections continue until a Governor is selected or there is only one
    # eligible candidate remaining (1.09.5)
    remaining = remaining_candidates(province, candidates, defeated_proposals)
    if not remaining:
        return False
    return not is_sole_candidate(province, vacant, candidates, defeated_proposals)


def governor_field_name(province_name: str) -> str:
    return f"Governor for {province_name}"
