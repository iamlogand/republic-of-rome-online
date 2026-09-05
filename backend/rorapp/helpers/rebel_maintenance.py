from typing import List, Optional

from rorapp.helpers.civil_war import get_civil_war
from rorapp.models import Campaign, Faction, Legion, Senator

MAINTENANCE_COST = 2


def rebel_campaign(game_id: int) -> Optional[Campaign]:
    war = get_civil_war(game_id)
    if not war or not war.primary_rebel:
        return None
    return Campaign.objects.filter(game=game_id, commander=war.primary_rebel).first()


def payable_rebel_legions(game_id: int) -> List[Legion]:
    """Rebel legions that cost maintenance, veterans of a rebel being free (1.11.35)."""

    campaign = rebel_campaign(game_id)
    if not campaign:
        return []
    return [
        l
        for l in Legion.objects.filter(game=game_id, campaign=campaign)
        .select_related("allegiance")
        .order_by("number")
        if not (l.veteran and l.allegiance and l.allegiance.rebel)
    ]


def rebel_paymasters(game_id: int) -> List[Senator]:
    """The rebel senators whose Personal Treasuries pay maintenance (1.11.35)."""

    war = get_civil_war(game_id)
    if not war or not war.primary_rebel:
        return []
    primary_rebel = war.primary_rebel
    others = (
        Senator.objects.filter(game=game_id, rebel=True, alive=True)
        .exclude(id=primary_rebel.id)
        .order_by("id")
    )
    return [primary_rebel] + list(others)


def rebel_faction(game_id: int) -> Optional[Faction]:
    war = get_civil_war(game_id)
    if not war or not war.primary_rebel or not war.primary_rebel.faction_id:
        return None
    return Faction.objects.filter(id=war.primary_rebel.faction_id).first()


def released_legions(game_id: int) -> List[Legion]:
    return list(Legion.objects.filter(game=game_id, released=True).order_by("number"))
