import os
import json
from typing import List
from django.conf import settings
from rorapp.functions.matching_war_helper import update_matching_wars
from rorapp.models import Action, ActionLog, War
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.serializers import (
    ActionLogSerializer,
    WarSerializer,
)


def create_new_war(action: Action, name: str) -> List[dict]:
    """
    Create a new war and activate any inactive matching wars.
    """

    messages_to_send = []

    # Get war data from JSON file
    war_json_path = os.path.join(settings.BASE_DIR, "rorapp", "presets", "war.json")
    with open(war_json_path, "r") as file:
        wars_dict = json.load(file)
    data = wars_dict[name]

    # Get matching wars
    matching_wars = War.objects.filter(
        game=action.step.phase.turn.game, name=data["name"]
    ).exclude(status="defeated")
    is_matched = matching_wars.exists()
    if is_matched:
        initial_status = "imminent"
    else:
        initial_status = "active" if data["immediately_active"] else "inactive"

    # Create war
    war = War(
        name=data["name"],
        index=data["index"],
        game=action.step.phase.turn.game,
        land_strength=data["land_strength"],
        fleet_support=data["fleet_support"],
        naval_strength=data["naval_strength"],
        disaster_numbers=data["disaster_numbers"],
        standoff_numbers=data["standoff_numbers"],
        spoils=data["spoils"],
        status=initial_status,
        famine=data["famine"],
        undefeated_navy=False if data["naval_strength"] > 0 else True,
    )
    war.save()
    messages_to_send.append(create_websocket_message("war", WarSerializer(war).data))

    # Create action log for new war
    action_log_index = (
        ActionLog.objects.filter(step__phase__turn__game=action.step.phase.turn.game.id)
        .order_by("index")
        .last()
        .index
        + 1
    )
    action_log_data = {
        "war": war.id,
        "initial_status": initial_status,
        "initiating_faction": action.faction.id,
    }
    if is_matched:
        action_log_data["matching_wars"] = [
            war.id for war in matching_wars.exclude(id=war.id)
        ]
    action_log = ActionLog(
        index=action_log_index,
        step=action.step,
        type="new_war",
        data=action_log_data,
    )
    action_log.save()
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

    # Activate matching wars
    if is_matched:
        first = True
        for matching_war in matching_wars.filter(status="inactive").order_by("index"):
            matching_war.status = "active" if first else "imminent"
            matching_war.save()
            messages_to_send.append(
                create_websocket_message("war", WarSerializer(matching_war).data)
            )

            # Create action log for matching war
            action_log_index += 1
            action_log = ActionLog(
                index=action_log_index,
                step=action.step,
                type="matched_war",
                data={
                    "war": matching_war.id,
                    "new_status": matching_war.status,
                    "new_war": war.id,
                },
            )
            action_log.save()
            messages_to_send.append(
                create_websocket_message(
                    "action_log", ActionLogSerializer(action_log).data
                )
            )

            first = False

    messages_to_send.extend(update_matching_wars(action.step.phase.turn.game.id))

    return messages_to_send
