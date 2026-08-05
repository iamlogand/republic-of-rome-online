from rorapp.helpers.governor_candidates import (
    get_eligible_governor_candidates,
    vacant_forum_provinces,
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


def parse_governor_proposal(proposal: str) -> tuple[str, str] | None:
    pairings = parse_governor_proposals(proposal)
    if not pairings or len(pairings) != 1:
        return None
    return pairings[0]


def defeated_governor_pairings(defeated_proposals: list[str]) -> set[str]:
    """
    Pairings locked by *single* defeated proposals only.

    A defeated joint proposal blocks reintroduction of that exact joint
    motion (via has_defeated_proposal) but does not lock the individual
    pairings for later separate votes (1.09.131).
    """
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
):
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


def has_governor_election_work_remaining(
    game_id: int,
    senators=None,
    defeated_proposals: list[str] | None = None,
) -> bool:
    """
    True when a vacant Forum province still has at least one non-defeated
    eligible candidate, including a last remaining candidate who must be
    appointed (1.09.5, 1.09.54).
    """
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
    """True when some vacant province still has two or more remaining candidates."""
    vacant, candidates, defeated_proposals = governor_election_inputs(
        game_id, senators, defeated_proposals
    )
    return any(
        len(remaining_candidates_for_province(province, candidates, defeated_proposals))
        >= 2
        for province in vacant
    )


def governor_field_name(province_name: str) -> str:
    return f"Governor for {province_name}"


def next_senate_sub_phase_after_prosecutions(game_id: int) -> str:
    if has_governor_election_work_remaining(game_id):
        return Game.SubPhase.GOVERNOR_ELECTION
    return Game.SubPhase.OTHER_BUSINESS


def next_senate_sub_phase_after_governor_election(game_id: int) -> str:
    if has_governor_election_work_remaining(game_id):
        return Game.SubPhase.GOVERNOR_ELECTION
    return Game.SubPhase.OTHER_BUSINESS


def assign_governor(province: Province, senator: Senator) -> None:
    province.governor = senator
    province.term = 3
    province.elected_this_turn = True
    province.save()

    senator.location = province.name
    senator.remove_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
    senator.save()


def clear_governorship(province: Province) -> None:
    province.governor = None
    province.term = None
    province.elected_this_turn = False
    province.save()
