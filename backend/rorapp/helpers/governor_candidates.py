from typing import List

from rorapp.models import Province, Senator

_MAJOR_OFFICES = [
    Senator.Title.DICTATOR,
    Senator.Title.MASTER_OF_HORSE,
    Senator.Title.ROME_CONSUL,
    Senator.Title.FIELD_CONSUL,
    Senator.Title.PROCONSUL,
    Senator.Title.CENSOR,
]


def holds_major_office(senator: Senator) -> bool:
    return any(senator.has_title(title) for title in _MAJOR_OFFICES)


def get_eligible_governor_candidates(senators) -> List[Senator]:
    return sorted(
        [
            s
            for s in senators
            if s.alive
            and s.location == "Rome"
            and not holds_major_office(s)
            and not s.has_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
        ],
        key=lambda s: s.family_name,
    )


def vacant_forum_provinces(game_id: int) -> List[Province]:
    return list(
        Province.objects.filter(game_id=game_id, governor__isnull=True).order_by("name")
    )


def has_vacant_forum_provinces(game_id: int) -> bool:
    return Province.objects.filter(game_id=game_id, governor__isnull=True).exists()
