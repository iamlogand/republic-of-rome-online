from typing import List, Optional, Tuple

from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.hrao import highest_ranking_senator, set_hrao
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.helpers.text import possessive
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Fleet, Game, Legion, Log, Senator, War

CIVIL_WAR_NAME = "Civil War"
CIVIL_WAR_LOCATION = "Italia"


def get_civil_war(game_id: int) -> Optional[War]:
    return (
        War.objects.filter(game=game_id, primary_rebel__isnull=False)
        .exclude(status=War.Status.DEFEATED)
        .first()
    )


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


def land_victors_in_declaration_order(
    game_state: GameStateLive | GameStateSnapshot,
) -> List[Campaign]:
    """Land victors starting with the HRAO's faction and proceeding clockwise (1.11.3)."""

    positions = {f.id: f.position for f in game_state.factions}
    campaigns = [
        c
        for c in game_state.campaigns
        if c.land_victory and c.commander and c.commander.faction_id in positions
    ]
    if not campaigns:
        return []

    # Declaration order assumes that every senator in play is in Rome (1.11.3)
    starting_senator = highest_ranking_senator(
        [s for s in game_state.senators if s.faction_id and s.alive]
    )
    order = sorted(positions.values())
    if starting_senator and starting_senator.faction_id in positions:
        start_index = order.index(positions[starting_senator.faction_id])
        order = order[start_index:] + order[:start_index]

    def declaration_key(campaign: Campaign) -> Tuple[int, int]:
        faction_id = campaign.commander.faction_id if campaign.commander else None
        return (order.index(positions[faction_id]) if faction_id else 0, campaign.id)

    return sorted(campaigns, key=declaration_key)


def declaring_campaign(
    game_state: GameStateLive | GameStateSnapshot, faction_id: int
) -> Optional[Campaign]:
    """The next land victor to declare, if he belongs to this faction (1.11.3)."""

    game = game_state.game
    if (
        game.phase != Game.Phase.REVOLUTION
        or game.sub_phase != Game.SubPhase.CIVIL_WAR_DECLARATION
    ):
        return None
    victors = land_victors_in_declaration_order(game_state)
    if not victors or not victors[0].commander:
        return None
    return victors[0] if victors[0].commander.faction_id == faction_id else None


def rollable_legions(campaign: Campaign) -> List[Legion]:
    """Legions that must roll to follow their commander into revolt (1.11.31)."""

    return [
        l
        for l in campaign.legions.all().order_by("number")
        if not (l.veteran and l.allegiance_id == campaign.commander_id)
    ]


def standing_rebel(game_id: int) -> Optional[Senator]:
    """The Primary Rebel, who keeps his marker even once his army is gone (1.11.3)."""

    war = get_civil_war(game_id)
    if war and war.primary_rebel:
        return war.primary_rebel
    return Senator.objects.filter(game=game_id, rebel=True, alive=True).first()


def revolt_available(campaign: Campaign) -> bool:
    """Whether a land victor may declare, given any standing rebel (1.11.3)."""

    if not campaign.commander or not campaign.commander.faction_id:
        return False
    rebel = standing_rebel(campaign.game_id)
    if not rebel:
        return True
    # Only one faction may be in revolt, and once a Primary Rebel has been
    # determined nobody else may revolt until he has been killed
    if rebel.faction_id == campaign.commander.faction_id:
        return False
    if not rebel.has_status_item(Senator.StatusItem.DECLARED_REVOLT):
        return False
    war = get_civil_war(campaign.game_id)
    if not war:
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

    # A Master of Horse who does not join the revolt returns to Rome (1.11.32)
    master_of_horse = campaign.master_of_horse
    if master_of_horse:
        master_of_horse.location = "Rome"
        master_of_horse.save()
        campaign.master_of_horse = None

    commander.rebel = True
    commander.location = CIVIL_WAR_LOCATION
    commander.add_status_item(Senator.StatusItem.DECLARED_REVOLT)
    commander.save()

    legions = list(campaign.legions.all().order_by("number"))
    log_text = f"{commander.display_name} declared himself in revolt and marched on Rome with "
    log_text += unit_list_to_string(legions, []) if legions else "no legions"
    log_text += "."
    if fleets:
        log_text += (
            f" {unit_list_to_string([], fleets)} played no part in the revolt and "
            "returned to the reserve forces."
        )
    if master_of_horse:
        log_text += f" {master_of_horse.display_name} returned to Rome."
    Log.create_object(game_id, log_text)

    displaced_war = get_civil_war(game_id)
    displaced_rebel = displaced_war.primary_rebel if displaced_war else None
    if displaced_war and displaced_rebel:
        displaced_rebel.rebel = False
        displaced_rebel.remove_status_item(Senator.StatusItem.DECLARED_REVOLT)
        displaced_rebel.save()
        Log.create_object(
            game_id,
            f"{commander.display_name} fielded the stronger army, so "
            f"{possessive(displaced_rebel.display_name)} declaration was ignored.",
        )
        for displaced_campaign in Campaign.objects.filter(
            game=game_id, war=displaced_war
        ).order_by("id"):
            lay_down_command(displaced_campaign)

    # The rebel has left Rome, so Rome needs a new highest official (1.09.11)
    set_hrao(game_id)

    # Only one Faction may be in Revolt, so there is only ever one Civil War (1.11.3)
    civil_war = displaced_war or War(
        game_id=game_id,
        name=CIVIL_WAR_NAME,
        index=0,
        fleet_support=0,
        naval_strength=0,
        spoils=0,
        location=CIVIL_WAR_LOCATION,
        status=War.Status.ACTIVE,
    )
    civil_war.primary_rebel = commander
    civil_war.land_strength = army_strength(campaign)
    civil_war.save()
    campaign.war = civil_war
    campaign.save()
