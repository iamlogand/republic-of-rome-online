import os
import json
from typing import List
from django.conf import settings
from rorapp.models import ActionLog, Faction, Game, Step, War
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.serializers import (
    ActionLogSerializer,
    WarSerializer,
)


def create_new_war(game_id: int, initiating_faction_id: int, name: str) -> List[dict]:
    """
    Create a new war and activate any inactive matching wars.
    
    Args:
        game_id (int): The game ID.
        initiating_faction_id (int): The faction that initiated the war situation.
        name (str): The name of the war.

    Returns:
        dict: The WebSocket messages to send.
    """
    
    game = Game.objects.get(id=game_id)
    faction = Faction.objects.get(id=initiating_faction_id)

    messages_to_send = []

    # Get war data from JSON file
    war_json_path = os.path.join(settings.BASE_DIR, "rorapp", "presets", "war.json")
    with open(war_json_path, "r") as file:
        wars_dict = json.load(file)
    data = wars_dict[name]

    # Get matching wars
    matching_wars = War.objects.filter(
        game=game, name=data["name"]
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
        game=game,
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
        ActionLog.objects.filter(step__phase__turn__game=game.id)
        .order_by("index")
        .last()
        .index
        + 1
    )
    action_log_data = {
        "war": war.id,
        "initial_status": initial_status,
        "initiating_faction": faction.id,
    }
    if is_matched:
        action_log_data["matching_wars"] = [
            war.id for war in matching_wars.exclude(id=war.id)
        ]
    latest_step = (
        Step.objects.filter(phase__turn__game=game_id).order_by("-index").first()
    )
    action_log = ActionLog(
        index=action_log_index,
        step=latest_step,
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
                step=latest_step,
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

    return messages_to_send
