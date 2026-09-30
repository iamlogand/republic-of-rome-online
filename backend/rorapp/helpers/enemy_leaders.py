from typing import Iterable, Optional

from django.db.models import Q, QuerySet

from rorapp.models import EnemyLeader, War


def get_matching_enemy_leaders(
    game_id: int, war: War, active: Optional[bool] = None
) -> QuerySet[EnemyLeader]:
    """Return Enemy Leaders associated with this War by series or individual War."""
    association = Q(war_name=war.name)
    if war.series_name:
        association |= Q(war_name__isnull=True, series_name=war.series_name)

    leaders = EnemyLeader.objects.filter(game=game_id).filter(association)
    if active is not None:
        leaders = leaders.filter(active=active)
    return leaders


def get_matching_wars(
    game_id: int,
    leader: EnemyLeader,
    statuses: Optional[Iterable[str]] = None,
) -> QuerySet[War]:
    """Return Wars associated with this Enemy Leader by series or individual War."""
    if leader.war_name:
        wars = War.objects.filter(game=game_id, name=leader.war_name)
    elif leader.series_name:
        wars = War.objects.filter(game=game_id, series_name=leader.series_name)
    else:
        wars = War.objects.none()

    if statuses is not None:
        wars = wars.filter(status__in=statuses)
    return wars.order_by("index")
