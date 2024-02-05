import os
import json
from typing import List
from django.conf import settings
from rorapp.models import ActionLog, Senator, SenatorActionLog, Action
from rorapp.functions.websocket_message_helper import create_websocket_message

from rorapp.serializers import (
    ActionLogSerializer,
    SenatorActionLogSerializer,
    SenatorSerializer,
)


def create_new_family(action: Action, name: str) -> List[dict]:
    """
    Add a new family senator to the senate.
    """

    messages_to_send = []

    # Get senator data from JSON file
    senator_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "presets", "senator.json"
    )
    with open(senator_json_path, "r") as file:
        senators_dict = json.load(file)
    senator_data = senators_dict[name]

    # Create senator
    senator = Senator(
        name=name,
        game=action.step.phase.turn.game,
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
    action_log_index = (
        ActionLog.objects.filter(step__phase__turn__game=action.step.phase.turn.game.id)
        .order_by("index")
        .last()
        .index
        + 1
    )
    action_log = ActionLog(
        index=action_log_index,
        step=action.step,
        type="new_family",
        data={"senator": senator.id, "initiating_faction": action.faction.id},
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
