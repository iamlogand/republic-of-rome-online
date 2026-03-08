from typing import List
from rorapp.models import Senator


def get_minor_prosecution_reasons(senator: Senator, defeated_proposals: List[str]) -> List[str]:
    """Return the list of valid minor prosecution reasons for a senator, excluding already-defeated ones."""
    reasons = []
    if senator.has_status_item(Senator.StatusItem.MAJOR_CORRUPT):
        reasons.append("corruption in office")
    for cc in senator.corrupt_concessions:
        formatted = f"corruption via {cc} concession"
        if formatted not in reasons:
            reasons.append(formatted)
    prefix = f"Prosecute {senator.display_name} for "
    failed_reasons = {p[len(prefix):] for p in defeated_proposals if p.startswith(prefix)}
    return [r for r in reasons if r not in failed_reasons]


def has_minor_prosecution_target(senators, defeated_proposals: List[str], censor_id: int) -> bool:
    """Return True if at least one senator is eligible to be accused in a minor prosecution."""
    for senator in senators:
        if not (senator.alive and senator.location == "Rome" and senator.faction and senator.id != censor_id):
            continue
        reasons = []
        if senator.has_status_item(Senator.StatusItem.MAJOR_CORRUPT):
            reasons.append("corruption in office")
        for cc in senator.corrupt_concessions:
            formatted = f"corruption via {cc} concession"
            if formatted not in reasons:
                reasons.append(formatted)
        if not reasons:
            continue
        prefix = f"Prosecute {senator.display_name} for "
        failed_reasons = {p[len(prefix):] for p in defeated_proposals if p.startswith(prefix)}
        if any(r for r in reasons if r not in failed_reasons):
            return True
    return False


def has_major_prosecution_target(senators, defeated_proposals: List[str], censor_id: int) -> bool:
    """Return True if at least one senator is eligible to be accused in a major prosecution."""
    for senator in senators:
        if not (senator.alive and senator.location == "Rome" and senator.faction and senator.id != censor_id):
            continue
        if senator.has_status_item(Senator.StatusItem.MAJOR_CORRUPT):
            proposal = f"Prosecute {senator.display_name} for major corruption in office"
            if proposal not in defeated_proposals:
                return True
    return False
