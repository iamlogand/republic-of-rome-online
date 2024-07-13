import os
import json
from django.conf import settings
from rorapp.functions.progress_helper import get_step
from rorapp.models import ActionLog, Faction, Game, Senator, SenatorActionLog
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.serializers import (
    ActionLogSerializer,
    SenatorActionLogSerializer,
    SenatorSerializer,
)


def create_new_family(initiating_faction_id: int, name: str) -> list[dict]:
    """
    Add a new family senator to the senate.

    Args:
        game_id (int): The game ID.
        initiating_faction_id (int): The faction that initiated the situation.
        name (str): The name of the family senator (e.g. "Cornelius").

    Returns:
        dict: The WebSocket messages to send.
    """

    faction = Faction.objects.get(id=initiating_faction_id)
    game_id = faction.game.id
    game = Game.objects.get(id=game_id)

    messages_to_send = []

    # Get senator data from JSON file
    senator_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "data", "senator.json"
    )
    with open(senator_json_path, "r") as file:
        senators_dict = json.load(file)
    senator_data = senators_dict[name]

    # Create senator
    senator = Senator(
        name=name,
        game=game,
        code=senator_data["code"],
        military=senator_data["military"],
        oratory=senator_data["oratory"],
        loyalty=senator_data["loyalty"],
        influence=senator_data["influence"],
    )
    senator.save()
    messages_to_send.append(
        create_websocket_message("senator", SenatorSerializer(senator).data)
    )

    # Create action log
    latest_action_log = (
        ActionLog.objects.filter(step__phase__turn__game=game.id)
        .order_by("index")
        .last()
    )
    assert isinstance(latest_action_log, ActionLog)
    action_log_index = latest_action_log.index + 1
    latest_step = get_step(game_id)
    action_log = ActionLog(
        index=action_log_index,
        step=latest_step,
        type="new_family",
        data={"senator": senator.id, "initiating_faction": faction.id},
    )
    action_log.save()
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

    # Create senator action log
    senator_action_log = SenatorActionLog(senator=senator, action_log=action_log)
    senator_action_log.save()
    messages_to_send.append(
        create_websocket_message(
            "senator_action_log", SenatorActionLogSerializer(senator_action_log).data
        )
    )

    return messages_to_send
