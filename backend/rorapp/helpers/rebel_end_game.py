from typing import List, Optional

from rorapp.helpers.civil_war import standing_rebel
from rorapp.helpers.text import format_list
from rorapp.models import Campaign, Fleet, Game, Legion, Log, Senator, War

# The rebel's Winning Conditions, in the order 1.12.2 lists them
BATTLE_WON = 1
REPUBLIC_COLLAPSED = 2

MAXIMUM_ACTIVE_WARS = 4


def rebel_faction_name(game_id: int) -> str:
    for rebel in [standing_rebel(game_id)] + list(
        Senator.objects.filter(game=game_id, rebel=True, alive=True)
    ):
        if rebel and rebel.faction:
            return rebel.faction.display_name
    return "the rebels"


def active_wars_against_rome(game_id: int) -> List[War]:
    """Active wars, less the Civil War of a rebel who has already won (1.12.1)."""

    wars = War.objects.filter(game=game_id, status=War.Status.ACTIVE)
    game = Game.objects.get(id=game_id)
    if game.rebel_winning_condition:
        wars = wars.filter(primary_rebel__isnull=True)
    return list(wars.order_by("id"))


def rebel_campaign(game_id: int) -> Optional[Campaign]:
    rebel = standing_rebel(game_id)
    if not rebel:
        return None
    return Campaign.objects.filter(game=game_id, commander=rebel).first()


def muster_every_force_for_the_rebel(game_id: int) -> None:
    """Hand the Primary Rebel every legion and fleet in play (1.12.3)."""

    rebel = standing_rebel(game_id)
    campaign = rebel_campaign(game_id)
    if not campaign and rebel:
        campaign = Campaign.objects.create(game_id=game_id, war=None, commander=rebel)
    if not campaign:
        return
    campaign.war = None
    campaign.land_victory = False
    campaign.save()

    returning: List[Senator] = []
    for other in Campaign.objects.filter(game=game_id).exclude(id=campaign.id):
        for senator in [other.commander, other.master_of_horse]:
            if senator and senator.alive:
                senator.location = "Rome"
                senator.save()
                returning.append(senator)
        other.delete()
    if returning:
        Log.create_object(
            game_id,
            f"{format_list([s.display_name for s in returning])} returned to Rome "
            "as Rome's armies were surrendered to the rebels.",
        )

    Legion.objects.filter(game=game_id).update(campaign=campaign)
    Fleet.objects.filter(game=game_id).update(campaign=campaign)
