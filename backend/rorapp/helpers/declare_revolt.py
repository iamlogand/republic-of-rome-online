from rorapp.helpers.force_strength import force_strength
from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.helpers.text import possessive
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Fleet, Log, Senator, War

REVOLT_LOCATION = "Italia"


def declare_revolt(campaign: Campaign) -> None:
    """Record a land victor's declaration of revolt (1.11.3)."""

    game_id = campaign.game_id
    commander = campaign.commander
    if not commander:
        return

    commander.rebel = True
    commander.add_status_item(Senator.StatusItem.DECLARED_REVOLT)
    commander.save()

    legions = list(campaign.legions.all().order_by("number"))
    army = unit_list_to_string(legions, []) if legions else "no legions"
    Log.create_object(
        game_id, f"{commander.display_name} declared himself in revolt with {army}."
    )

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
            f"{commander.display_name} fielded the stronger rebel army, so "
            f"{possessive(displaced_rebel.display_name)} declaration was ignored.",
        )
        lay_down_command(displaced_war.campaigns.get())
        # Senators returning to Rome may outrank the HRAO (1.09.11)
        set_hrao(game_id)

    # Only one Faction may be in Revolt at a time (1.11.3)
    revolt = displaced_war or War(
        game_id=game_id,
        name="Revolt",
        index=0,
        fleet_support=0,
        naval_strength=0,
        spoils=0,
        location=REVOLT_LOCATION,
        status=War.Status.ACTIVE,
    )
    revolt.primary_rebel = commander
    revolt.land_strength = force_strength(
        sum(l.strength for l in legions), commander.military
    )
    revolt.save()
    campaign.war = revolt
    campaign.save()


def march_on_rome(campaign: Campaign) -> None:
    """Send the Primary Rebel on Rome once nobody can displace him (1.11.3)."""

    game_id = campaign.game_id
    commander = campaign.commander
    if not commander:
        return

    commander.location = REVOLT_LOCATION
    commander.save()

    # Fleets play no role in a revolt (1.11.3)
    fleets = list(Fleet.objects.filter(campaign=campaign).order_by("number"))
    for fleet in fleets:
        fleet.campaign = None
    Fleet.objects.bulk_update(fleets, ["campaign"])

    # The Master of Horse keeps his office and returns to Rome (1.11.32)
    master_of_horse = campaign.master_of_horse
    if master_of_horse:
        master_of_horse.location = "Rome"
        master_of_horse.save()
        campaign.master_of_horse = None
        campaign.save()

    log_text = f"{commander.display_name} marched on Rome."
    if master_of_horse:
        log_text += f" {master_of_horse.display_name} returned to Rome."
    if fleets:
        log_text += (
            f" {unit_list_to_string([], fleets)} played no part in the revolt and "
            "returned to the reserve forces."
        )
    Log.create_object(game_id, log_text)

    if master_of_horse:
        # Senators returning to Rome may outrank the HRAO (1.09.11)
        set_hrao(game_id)
