import os
import json
from typing import List
from django.conf import settings
from rorapp.functions.progress_helper import get_latest_step
from rorapp.models import ActionLog, EnemyLeader, Faction, Game, War
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.serializers import (
    ActionLogSerializer,
    EnemyLeaderSerializer,
    WarSerializer,
)


def create_new_war(initiating_faction_id: int, name: str) -> List[dict]:
    """
    Create a new war and activate any inactive matching wars.

    Args:
        game_id (int): The game ID.
        initiating_faction_id (int): The faction that initiated the situation.
        name (str): The full name of the war (e.g. "2nd Punic War").

    Returns:
        dict: The WebSocket messages to send.
    """

    faction = Faction.objects.get(id=initiating_faction_id)
    game_id = faction.game.id
    game = Game.objects.get(id=game_id)

    messages_to_send = []

    # Get war data from JSON file
    war_json_path = os.path.join(settings.BASE_DIR, "rorapp", "data", "war.json")
    with open(war_json_path, "r") as file:
        wars_dict = json.load(file)
    data = wars_dict[name]

    # Get matching wars
    matching_wars = War.objects.filter(game=game, name=data["name"]).exclude(
        status="defeated"
    )
    is_matched_by_war = matching_wars.exists()
    if is_matched_by_war:
        initial_status = "imminent"
    else:
        initial_status = "active" if data["immediately_active"] else "inactive"

    # Get matching enemy leaders
    matching_enemy_leaders = EnemyLeader.objects.filter(
        game=game, war_name=data["name"], current_war=None
    ).exclude(dead=True)
    is_activated_by_enemy_leader = False
    if matching_enemy_leaders.exists() and initial_status == "inactive":
        is_activated_by_enemy_leader = True
        initial_status = "active"

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
    if is_matched_by_war:
        action_log_data["matching_wars"] = [
            war.id for war in matching_wars.exclude(id=war.id)
        ]
    if is_activated_by_enemy_leader:
        # These are any enemy leader(s) that were idle but have matched and are responsible
        # for activating this war because the war was not inherently active
        action_log_data["activating_enemy_leaders"] = [
            leader.id for leader in matching_enemy_leaders
        ]
    latest_step = get_latest_step(game_id)
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
    if is_matched_by_war:
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

    # Activate matching enemy leaders
    if matching_enemy_leaders.exists():
        for enemy_leader in matching_enemy_leaders:
            enemy_leader.current_war = war
            enemy_leader.save()
            messages_to_send.append(
                create_websocket_message(
                    "enemy_leader", EnemyLeaderSerializer(enemy_leader).data
                )
            )

            # Create action log for matching enemy leader
            action_log_index += 1
            action_log = ActionLog(
                index=action_log_index,
                step=latest_step,
                type="matched_enemy_leader",
                data={
                    "enemy_leader": enemy_leader.id,
                    "new_war": war.id,
                },
            )
            action_log.save()
            messages_to_send.append(
                create_websocket_message(
                    "action_log", ActionLogSerializer(action_log).data
                )
            )

    return messages_to_send
