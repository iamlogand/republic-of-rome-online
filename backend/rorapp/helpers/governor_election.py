from rorapp.helpers.governor_candidates import (
    get_eligible_governor_candidates,
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


def is_exclusive_last_remaining_candidate(
    province: Province,
    vacant: list[Province],
    candidates: list[Senator],
    defeated_proposals: list[str],
) -> bool:
    """
    True when this province has exactly one remaining candidate who is not
    also the sole remaining candidate for another vacant province.

    A last remaining candidate for a single province is appointed (1.09.5).
    If the same senator is the last remaining candidate for more than one
    vacant province, the Senate must still choose which province they take
    (1.09.54).
    """
    remaining = remaining_candidates_for_province(
        province, candidates, defeated_proposals
    )
    if len(remaining) != 1:
        return False
    sole = remaining[0]
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
    """True when some vacant province still needs a Senate vote."""
    vacant, candidates, defeated_proposals = governor_election_inputs(
        game_id, senators, defeated_proposals
    )
    return any(
        needs_governor_election_vote(
            province, vacant, candidates, defeated_proposals
        )
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
    if was_hrao:
        senator.remove_title(Senator.Title.HRAO)
    if was_presiding_magistrate:
        senator.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
    senator.save()

    if was_hrao:
        set_hrao(province.game_id)
    if was_presiding_magistrate:
        transfer_presiding_magistrate_to_hrao(province.game_id)


def clear_governorship(province: Province) -> None:
    province.governor = None
    province.term = None
    province.elected_this_turn = False
    province.save()
