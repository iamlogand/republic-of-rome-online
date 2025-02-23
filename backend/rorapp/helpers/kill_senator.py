import json
import os
import re
from django.conf import settings
from rorapp.models import Senator


def kill_senator(game_id: int, senator_id: int):

    senator = Senator.objects.get(game=game_id, id=senator_id)

    senator.popularity = 0
    senator.knights = 0
    senator.talents = 0

    if senator.has_title(Senator.Title.FACTION_LEADER):
        senator.titles = [Senator.Title.FACTION_LEADER.value]
    else:
        senator.alive = False
        senator.faction = None
        senator.titles = []

    senator_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "data", "senator.json"
    )
    with open(senator_json_path, "r") as file:
        senators_dict = json.load(file)
        for senator_name, senator_data in senators_dict.items():
            match = re.match(r"(\d+)([A-Z]?)", senator.code)
            if match:
                code_number = int(match.group(1))
                if senator_data["code"] == code_number:
                    senator.influence = senator_data["influence"]
                    break

    senator.save()
