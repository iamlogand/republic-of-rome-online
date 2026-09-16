from rorapp.helpers.civil_war import army_strength
from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.helpers.text import possessive
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Fleet, Log, Senator, War

CIVIL_WAR_LOCATION = "Italia"


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
    Log.create_object(game_id, log_text)

    displaced_war = (
        War.objects.filter(game=game_id, primary_rebel__isnull=False)
        .exclude(status=War.Status.DEFEATED)
        .select_related("primary_rebel")
        .first()
    )
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
        name="Civil War",
        index=0,
        fleet_support=0,
        naval_strength=0,
        spoils=0,
        location=CIVIL_WAR_LOCATION,
        status=War.Status.ACTIVE,
    )
    civil_war.primary_rebel = commander
    civil_war.land_strength = army_strength(legions, commander.military)
    civil_war.save()
    campaign.war = civil_war
    campaign.save()
