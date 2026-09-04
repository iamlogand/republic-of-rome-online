from typing import List

from rorapp.helpers.text import format_list
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Fleet, Legion, Log, Senator


def lay_down_command(campaign: Campaign) -> None:
    """Return a land victor and his force to Rome (1.11.3)."""

    returning_senators: List[Senator] = []
    commander = campaign.commander
    if commander:
        commander.location = "Rome"
        commander.remove_title(Senator.Title.PROCONSUL)
        commander.save()
        returning_senators.append(commander)
    master_of_horse = campaign.master_of_horse
    if master_of_horse:
        master_of_horse.location = "Rome"
        master_of_horse.save()
        returning_senators.append(master_of_horse)

    legions = list(Legion.objects.filter(campaign=campaign).order_by("number"))
    fleets = list(Fleet.objects.filter(campaign=campaign).order_by("number"))
    campaign.delete()

    log_text = ""
    if returning_senators:
        names = format_list([s.display_name for s in returning_senators])
        log_text += f"{names} laid down command and returned to Rome."
    if legions or fleets:
        if log_text:
            log_text += " "
        log_text += (
            f"{unit_list_to_string(legions, fleets)} returned to the reserve forces."
        )
    if log_text:
        Log.create_object(campaign.game_id, log_text)
