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


def is_land_bill_assassination(game: Game) -> bool:
    """
    True while a land bill with same-faction sponsors is on the floor, when only
    its sponsors may be targeted and a caught assassin brings no consequences on
    his faction (1.09.623).
    """

    if not game.current_proposal or "land bill" not in game.current_proposal.lower():
        return False
    sponsors = list(
        Senator.objects.filter(
            game=game,
            alive=True,
            status_items__contains=Senator.StatusItem.NAMED_IN_PROPOSAL.value,
        )
    )
    if len(sponsors) < 2:
        return False
    return all(s.faction_id == sponsors[0].faction_id for s in sponsors[1:])
