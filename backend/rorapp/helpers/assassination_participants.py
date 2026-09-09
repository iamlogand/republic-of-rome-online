from typing import List, Optional, Tuple

from rorapp.models import Game, Senator


def get_assassination_participants(
    senators: List[Senator],
) -> Tuple[Optional[Senator], Optional[Senator]]:
    """Find the assassin and target from the given senator list by status items."""
    assassin = next(
        (s for s in senators if s.has_status_item(Senator.StatusItem.ASSASSIN)),
        None,
    )
    target = next(
        (
            s
            for s in senators
            if s.has_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
        ),
        None,
    )
    return assassin, target


def is_land_bill_assassination(game: Game, target: Senator) -> bool:
    """
    True for an attempt on a sponsor of a land bill whose sponsors share a
    faction, the only attempt on which a caught assassin brings no consequences
    on his faction (1.09.623). A land bill suspended for a special major
    prosecution (1.09.74) is still the business before the senate, so read the
    proposal and its sponsors from the stash whenever there is one.
    """

    stash = game.suspended_proposal or {}
    proposal = stash.get("current_proposal") or game.current_proposal
    if not proposal or "land bill" not in proposal.lower():
        return False

    named = stash.get("senators") or {
        str(s.id): s.status_items
        for s in Senator.objects.filter(game=game, alive=True)
    }
    sponsor_ids = {
        int(senator_id)
        for senator_id, status_items in named.items()
        if Senator.StatusItem.NAMED_IN_PROPOSAL.value in status_items
    }
    if target.id not in sponsor_ids:
        return False

    sponsors = list(Senator.objects.filter(game=game, alive=True, id__in=sponsor_ids))
    if len(sponsors) < 2:
        return False
    return all(s.faction_id == sponsors[0].faction_id for s in sponsors[1:])
