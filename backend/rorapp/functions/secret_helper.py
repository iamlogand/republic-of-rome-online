import os
import json
from typing import List
from django.conf import settings
from rorapp.functions.progress_helper import get_step
from rorapp.models import ActionLog, Faction, Game, Player, Secret
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.serializers import (
    ActionLogSerializer,
    SecretPrivateSerializer,
    SecretPublicSerializer,
)


def create_new_secret(initiating_faction_id: int, name: str) -> List[dict]:
    """
    Create a new secret and give it to the initiating faction.

    Args:
        game_id (int): The game ID.
        initiating_faction_id (int): The faction that initiated the situation.
        name (str): The name of the secret (e.g. "P. Cornelius Scipio Africanus").

    Returns:
        dict: The WebSocket messages to send.
    """

    faction = Faction.objects.get(id=initiating_faction_id)
    assert isinstance(faction, Faction)
    assert isinstance(faction.player, Player)
    game_id = faction.game.id
    game = Game.objects.get(id=game_id)

    messages_to_send = []

    # Get secret data from JSON file
    situation_json_path = os.path.join(
        settings.BASE_DIR, "rorapp", "data", "situation.json"
    )
    with open(situation_json_path, "r") as file:
        situations_dict = json.load(file)
    if name in situations_dict:
        secret_type = situations_dict[name]["type"]
    else:
        secret_type = "statesman"

    # Create secret
    secret = Secret(
        name=name,
        type=secret_type,
        faction=faction,
    )
    secret.save()
    messages_to_send.append(
        create_websocket_message(
            "secret", SecretPrivateSerializer(secret).data, faction.player.id
        )
    )
    messages_to_send.append(
        create_websocket_message("secret", SecretPublicSerializer(secret).data)
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
        type="new_secret",
        faction=faction,
    )
    action_log.save()
    messages_to_send.append(
        create_websocket_message("action_log", ActionLogSerializer(action_log).data)
    )

    return messages_to_send
