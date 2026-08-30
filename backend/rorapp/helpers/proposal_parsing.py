from typing import Optional
from rorapp.models import Senator

LAND_BILL_PASS_PREFIX = "Pass type "
LAND_BILL_REPEAL_PREFIX = "Repeal type "


def extract_master_of_horse(remainder_after_name: str, senators) -> Optional[Senator]:
    """If remainder starts with ' and {senator display name}', return that senator."""
    if remainder_after_name.startswith(" and "):
        name_and_more = remainder_after_name[len(" and "):]
        return next(
            (s for s in senators if name_and_more.startswith(s.display_name)),
            None,
        )
    return None


def is_land_bill_proposal(proposal: Optional[str]) -> bool:
    """True while the passage or repeal of a land bill is on the floor (§1.09.62)."""
    if not proposal:
        return False
    return proposal.startswith(LAND_BILL_PASS_PREFIX) or proposal.startswith(
        LAND_BILL_REPEAL_PREFIX
    )
