import json
import os
import re
from django.conf import settings
from enum import Enum

from rorapp.helpers.hrao import set_new_hrao
from rorapp.models import Faction, Game, Log, Senator


class CauseOfDeath(Enum):
    NATURAL = "natural"


def kill_senator(
    game_id: int, senator_id: int, cause_of_death: CauseOfDeath = CauseOfDeath.NATURAL
):

    game = Game.objects.get(id=game_id)
    senator = Senator.objects.get(game=game_id, id=senator_id)
    faction = (
        Faction.objects.get(game=game_id, id=senator.faction.id)
        if senator.faction
        else None
    )
    senator_display_name = senator.display_name
    was_hrao = senator.has_title(Senator.Title.HRAO)

    senator.popularity = 0
    senator.knights = 0
    senator.talents = 0
    senator.generation += 1

    # Handle differently depending on whether senator was faction leader
    was_faction_leader = False
    if senator.has_title(Senator.Title.FACTION_LEADER):
        senator.titles = [Senator.Title.FACTION_LEADER.value]
        was_faction_leader = True
    else:
        senator.alive = False
        senator.faction = None
        senator.titles = []

    # Reset influence to default value for this senator
    senator_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "data", "senator.json"
    )
    with open(senator_json_path, "r") as file:
        senators_dict = json.load(file)
        for senator_data in senators_dict.values():
            match = re.match(r"(\d+)([A-Z]?)", senator.code)
            if match:
                code_number = int(match.group(1))
                if senator_data["code"] == code_number:
                    senator.influence = senator_data["influence"]
                    break

    senator.save()

    # Build log text
    if faction:
        log_text = f"{senator_display_name} of {faction.display_name}"
    else:
        log_text = f"The unaligned senator {senator_display_name}"

    if cause_of_death == CauseOfDeath.NATURAL:
        log_text += " died of natural causes."

    if was_faction_leader:
        log_text += (
            f" His heir {senator.display_name} replaced him as faction leader."
        )
    Log.create_object(game_id=game.id, text=log_text)

    # Handle HRAO death by setting new HRAO
    if was_hrao:
        set_new_hrao(game_id)
