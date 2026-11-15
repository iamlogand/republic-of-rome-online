from typing import List, Optional, Tuple
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


def extract_land_bill_sponsors(
    proposal: str, senators: List[Senator]
) -> Tuple[Optional[Senator], Optional[Senator]]:
    """Find sponsors in the supplied living senators, returning None for missing matches."""
    sponsored_by = " sponsored by "
    sponsor_start = proposal.index(sponsored_by) + len(sponsored_by)
    sponsor_name_and_more = proposal[sponsor_start:]
    sponsor = next(
        (s for s in senators if sponsor_name_and_more.startswith(s.display_name)),
        None,
    )
    cosponsor: Optional[Senator] = None
    if proposal.startswith(LAND_BILL_PASS_PREFIX):
        cosponsor_marker = " and co-sponsored by "
        cosponsor_start = proposal.index(cosponsor_marker) + len(cosponsor_marker)
        cosponsor_name = proposal[cosponsor_start:]
        cosponsor = next(
            (s for s in senators if cosponsor_name.startswith(s.display_name)),
            None,
        )
    return sponsor, cosponsor


def is_land_bill_proposal(proposal: Optional[str]) -> bool:
    """True while the passage or repeal of a land bill is on the floor (§1.09.62)."""
    if not proposal:
        return False
    return proposal.startswith(LAND_BILL_PASS_PREFIX) or proposal.startswith(
        LAND_BILL_REPEAL_PREFIX
    )
