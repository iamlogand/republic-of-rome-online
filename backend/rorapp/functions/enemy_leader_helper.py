import os
import json
from typing import List
from django.conf import settings
from rorapp.functions.progress_helper import get_step
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.models import ActionLog, EnemyLeader, Faction, Game, War
from rorapp.serializers import ActionLogSerializer, EnemyLeaderSerializer, WarSerializer


def create_new_enemy_leader(initiating_faction_id: int, name: str) -> List[dict]:
    """
    Create a new enemy leader. If there is a matching war, the leader joins it. If the matching war is not active then he activates it.

    Args:
        game_id (int): The game ID.
        initiating_faction_id (int): The faction that initiated the enemy leader situation.
        name (str): The name of the enemy leader (e.g. "Hannibal").

    Returns:
        dict: The WebSocket messages to send.
    """

    faction = Faction.objects.get(id=initiating_faction_id)
    game_id = faction.game.id
    game = Game.objects.get(id=game_id)

    messages_to_send = []

    # Get enemy leader data from JSON file
    enemy_leader_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "data", "enemy_leader.json"
    )
    with open(enemy_leader_json_path, "r") as file:
        enemy_leader_dict = json.load(file)
    data = enemy_leader_dict[name]

    # Get and active the matching war
    matching_war, activated_war_message = get_and_activate_matching_war(
        game, data["war_name"]
    )
    messages_to_send.extend(activated_war_message)

    # Create enemy leader
    enemy_leader = EnemyLeader(
        name=name,
        game=game,
        strength=data["strength"],
        disaster_number=data["disaster_number"],
        standoff_number=data["standoff_number"],
        war_name=data["war_name"],
        current_war=matching_war,
    )
    enemy_leader.save()
    messages_to_send.append(
        create_websocket_message(
            "enemy_leader", EnemyLeaderSerializer(enemy_leader).data
        )
    )

    # Create action log for new leader
    action_log = (
        ActionLog.objects.filter(step__phase__turn__game=game.id)
        .order_by("index")
        .last()
    )
    assert isinstance(action_log, ActionLog)
    action_log_index = action_log.index + 1
    latest_step = get_step(game_id)
    action_log_data = {
        "enemy_leader": enemy_leader.id,
        "matching_war": matching_war.id if matching_war else None,
        "initiating_faction": faction.id,
    }
    action_log = ActionLog(
        index=action_log_index,
        step=latest_step,
        type="new_enemy_leader",
        data=action_log_data,
    )
    action_log.save()
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

    # Create action log for matching war
    if matching_war:
        action_log_index += 1
        action_log = ActionLog(
            index=action_log_index,
            step=latest_step,
            type="matched_war",
            data={
                "war": matching_war.id,
                "new_status": matching_war.status,
                "new_enemy_leader": enemy_leader.id,
            },
        )
        action_log.save()
        messages_to_send.append(
            create_websocket_message("action_log", ActionLogSerializer(action_log).data)
        )

    return messages_to_send


def get_and_activate_matching_war(
    game: Game, war_name: int
) -> tuple[War | None, List[dict]]:
    """
    Get the matching war to link to the enemy leader. Activate it if it is inactive.
    """
    messages_to_send = []
    matching_wars = (
        War.objects.filter(game=game, name=war_name)
        .exclude(status__in=["imminent", "defeated"])
        .order_by("index")
    )
    war = None
    if matching_wars.exists():
        active_matching_wars = matching_wars.exclude(status="inactive")
        if active_matching_wars.exists():
            # The matching war is active or unprosecuted
            war = active_matching_wars.first()
        else:
            # If the matching war is inactive, activate it
            war = matching_wars.first()
            assert isinstance(war, War)
            war.status = "active"
            war.save()
            messages_to_send.append(
                create_websocket_message("war", WarSerializer(war).data)
            )

    return war, messages_to_send
