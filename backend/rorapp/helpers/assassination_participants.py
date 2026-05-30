from typing import List, Optional, Tuple

from rorapp.models import Senator


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
