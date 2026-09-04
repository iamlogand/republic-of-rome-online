from typing import List, Optional

from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.hrao import highest_ranking_senator
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.helpers.text import possessive
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Faction, Fleet, Game, Legion, Log, Senator, War

CIVIL_WAR_NAME = "Civil War"
CIVIL_WAR_LOCATION = "Italia"


def get_civil_war(game_id: int) -> Optional[War]:
    return War.objects.filter(game=game_id, primary_rebel__isnull=False).first()


def army_strength(campaign: Campaign) -> int:
    """Strength of an army, with the commander's Military rating capped by it (1.11.37)."""

    legion_strength = sum(l.strength for l in campaign.legions.all())
    military = campaign.commander.military if campaign.commander else 0
    if campaign.master_of_horse and campaign.master_of_horse.rebel:
        military += campaign.master_of_horse.military
    return legion_strength + min(military, legion_strength)


def refresh_civil_war_strength(game_id: int) -> None:
    war = get_civil_war(game_id)
    if not war or not war.primary_rebel:
        return
    campaign = Campaign.objects.filter(
        game=game_id, commander=war.primary_rebel
    ).first()
    war.land_strength = army_strength(campaign) if campaign else 0
    war.save()


def land_victors_in_declaration_order(game_id: int) -> List[Campaign]:
    """Land victors starting with the HRAO's faction and proceeding clockwise (1.11.3)."""

    campaigns = [
        c
        for c in Campaign.objects.filter(game=game_id, land_victory=True)
        .select_related("commander", "commander__faction")
        .order_by("id")
        if c.commander and c.commander.faction
    ]
    if not campaigns:
        return []

    # Declaration order assumes that every senator in play is in Rome (1.11.3)
    starting_senator = highest_ranking_senator(
        list(Senator.objects.filter(game=game_id, faction__isnull=False, alive=True))
    )
    positions = sorted(f.position for f in Faction.objects.filter(game=game_id))
    start = (
        starting_senator.faction.position
        if starting_senator and starting_senator.faction
        else positions[0]
    )
    start_index = positions.index(start)
    order = positions[start_index:] + positions[:start_index]

    def declaration_key(campaign: Campaign) -> tuple:
        faction = campaign.commander.faction if campaign.commander else None
        return (order.index(faction.position) if faction else 0, campaign.id)

    return sorted(campaigns, key=declaration_key)


def next_land_victor(game_id: int) -> Optional[Campaign]:
    victors = land_victors_in_declaration_order(game_id)
    return victors[0] if victors else None


def declaring_faction(
    game_state: GameStateLive | GameStateSnapshot, faction_id: int
) -> Optional[Faction]:
    """The faction whose commander is next to declare, if it is this one (1.11.3)."""

    faction = game_state.get_faction(faction_id)
    if not faction or not (
        game_state.game.phase == Game.Phase.REVOLUTION
        and game_state.game.sub_phase == Game.SubPhase.CIVIL_WAR_DECLARATION
    ):
        return None
    campaign = next_land_victor(faction.game_id)
    if not campaign or not campaign.commander:
        return None
    return faction if campaign.commander.faction_id == faction.id else None


def rollable_legions(campaign: Campaign) -> List[Legion]:
    """Legions that must roll to follow their commander into revolt (1.11.31)."""

    return [
        l
        for l in campaign.legions.all().order_by("number")
        if not (l.veteran and l.allegiance_id == campaign.commander_id)
    ]


def revolt_available(campaign: Campaign) -> bool:
    """Whether a land victor may declare, given any standing rebel (1.11.3)."""

    war = get_civil_war(campaign.game_id)
    if not war or not war.primary_rebel:
        return True
    if not campaign.commander or not campaign.commander.faction:
        return False
    # Only one faction may be in revolt, and only a stronger army displaces it
    if war.primary_rebel.faction_id == campaign.commander.faction_id:
        return False
    return army_strength(campaign) > war.land_strength


def declare_civil_war(campaign: Campaign) -> None:
    """Turn a land victor's army into the Civil War of his revolt (1.11.3)."""

    game_id = campaign.game_id
    commander = campaign.commander
    if not commander:
        return

    # Fleets play no role in a Civil War (1.11.3)
    fleets = list(Fleet.objects.filter(campaign=campaign).order_by("number"))
    for fleet in fleets:
        fleet.campaign = None
    Fleet.objects.bulk_update(fleets, ["campaign"])

    commander.rebel = True
    commander.location = CIVIL_WAR_LOCATION
    commander.save()
    campaign.land_victory = False
    campaign.save()

    legions = list(campaign.legions.all().order_by("number"))
    log_text = f"{commander.display_name} declared himself in revolt and is marching on Rome with "
    log_text += unit_list_to_string(legions, []) if legions else "no legions"
    log_text += "."
    if fleets:
        log_text += (
            f" {unit_list_to_string([], fleets)} played no part in the revolt and "
            "returned to the reserve forces."
        )
    Log.create_object(game_id, log_text)

    displaced_war = get_civil_war(game_id)
    displaced_rebel = displaced_war.primary_rebel if displaced_war else None
    if displaced_war and displaced_rebel:
        displaced_campaign = Campaign.objects.filter(
            game=game_id, commander=displaced_rebel
        ).first()
        displaced_war.delete()
        displaced_rebel.rebel = False
        displaced_rebel.save()
        Log.create_object(
            game_id,
            f"{commander.display_name} fielded the stronger army, so "
            f"{possessive(displaced_rebel.display_name)} declaration was ignored.",
        )
        if displaced_campaign:
            lay_down_command(displaced_campaign)

    War.objects.create(
        game=Game.objects.get(id=game_id),
        name=CIVIL_WAR_NAME,
        index=0,
        land_strength=army_strength(campaign),
        fleet_support=0,
        naval_strength=0,
        spoils=0,
        location=CIVIL_WAR_LOCATION,
        status=War.Status.ACTIVE,
        primary_rebel=commander,
    )
