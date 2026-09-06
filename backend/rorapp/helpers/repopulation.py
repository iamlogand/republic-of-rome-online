from typing import Iterable, List, Optional

from rorapp.classes.random_resolver import RandomResolver
from rorapp.models import Faction, Senator

SENATORS_REQUIRED_IN_ROME = 8


def count_aligned_senators_in_rome(senators: Iterable[Senator]) -> int:
    return sum(
        1
        for senator in senators
        if senator.alive and senator.faction_id and senator.location == "Rome"
    )


def senators_awaiting_promotion(senators: Iterable[Senator]) -> List[Senator]:
    return sorted(
        (
            senator
            for senator in senators
            if not senator.alive
            and senator.family
            and senator.curia_position is not None
        ),
        key=lambda senator: senator.curia_position or 0,
    )


def unaligned_senators_in_rome(senators: Iterable[Senator]) -> List[Senator]:
    return [
        senator
        for senator in senators
        if senator.alive and not senator.faction_id and senator.location == "Rome"
    ]


def faction_to_receive_senator(
    factions: Iterable[Faction],
    senators: Iterable[Senator],
    random_resolver: RandomResolver,
) -> Optional[Faction]:
    faction_list = list(factions)
    senator_list = list(senators)
    if not faction_list:
        return None

    def senator_count(faction: Faction) -> int:
        return sum(
            1
            for senator in senator_list
            if senator.alive and senator.faction_id == faction.id
        )

    def influence_in_rome(faction: Faction) -> int:
        return sum(
            senator.influence
            for senator in senator_list
            if senator.alive
            and senator.faction_id == faction.id
            and senator.location == "Rome"
        )

    fewest_senators = min(senator_count(f) for f in faction_list)
    candidates = [f for f in faction_list if senator_count(f) == fewest_senators]

    if len(candidates) > 1:
        least_influence = min(influence_in_rome(f) for f in candidates)
        candidates = [f for f in candidates if influence_in_rome(f) == least_influence]

    while len(candidates) > 1:
        rolls = {f.id: random_resolver.roll_dice() for f in candidates}
        highest_roll = max(rolls.values())
        candidates = [f for f in candidates if rolls[f.id] == highest_roll]

    return candidates[0]
