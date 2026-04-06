from typing import List
from rorapp.models import Senator

# Major offices that disqualify a senator from being Censor (Censor itself is exempt)
_DISQUALIFYING_OFFICES = [
    Senator.Title.ROME_CONSUL,
    Senator.Title.FIELD_CONSUL,
    Senator.Title.PROCONSUL,
]


def _holds_disqualifying_office(senator: Senator) -> bool:
    return any(senator.has_title(t) for t in _DISQUALIFYING_OFFICES)


def get_eligible_censor_candidates(senators) -> tuple[List[Senator], bool]:
    """
    Return (candidates, is_fallback) per §1.09.4.

    Primary pool: alive, in Rome, has faction, prior consul, no disqualifying major office.
    Fallback pool (if primary empty): alive, in Rome, has faction.

    is_fallback=True means the fallback (open election) is in use.
    """
    in_rome = [s for s in senators if s.alive and s.location == "Rome" and s.faction]

    primary = [
        s
        for s in in_rome
        if s.has_title(Senator.Title.PRIOR_CONSUL)
        and not _holds_disqualifying_office(s)
    ]

    if primary:
        return primary, False
    return in_rome, True
