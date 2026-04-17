from typing import List
from rorapp.models import Senator


def _holds_disqualifying_office(senator: Senator) -> bool:
    return any(
        senator.has_title(t)
        for t in [
            Senator.Title.ROME_CONSUL,
            Senator.Title.FIELD_CONSUL,
            Senator.Title.PROCONSUL,
        ]
    )


def get_eligible_dictator_candidates(senators) -> List[Senator]:
    return [
        s
        for s in senators
        if s.alive
        and s.location == "Rome"
        and s.faction
        and not _holds_disqualifying_office(s)
    ]


def get_eligible_master_of_horse_candidates(
    senators, dictator_id: int
) -> List[Senator]:
    return [
        s
        for s in senators
        if s.alive
        and s.location == "Rome"
        and s.faction
        and not _holds_disqualifying_office(s)
        and s.id != dictator_id
    ]
