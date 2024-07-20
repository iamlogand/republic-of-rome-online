from typing import List
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_websocket_messages(id: int, messages: List[dict]) -> None:
    """
    Send websocket messages to a game group and/or player groups.
    """

    channel_layer = get_channel_layer()
    game_messages = []
    player_messages: dict[str, list] = {}

    for message in messages:
        if "target_player_id" in message:
            target_player_id = message["target_player_id"]
            if target_player_id in player_messages:
                player_messages[target_player_id].append(message)
            else:
                player_messages[target_player_id] = [message]
        else:
            game_messages.append(message)

    if len(game_messages) > 0:
        # Send the messages to a game group, which will be broadcasted to all players and spectators connected to the game
        async_to_sync(channel_layer.group_send)(
            f"game_{id}", {"type": "game_update", "messages": game_messages}
        )
    if len(player_messages) > 0:
        # Send the messages to player groups, which will be sent to individual players only
        for target_player_id, messages in player_messages.items():
            async_to_sync(channel_layer.group_send)(
                f"player_{target_player_id}",
                {"type": "player_update", "messages": messages},
            )


def create_websocket_message(
    class_name: str, instance: object, target_player_id: int | None = None
) -> dict:
    """
    Make a WebSocket message for communicating to the frontend that an instance has been created or updated.

    Args:
        class_name (str): The class name of the instance.
        instance (object): The instance.

    Returns:
        dict: The WebSocket message.
    """

    message: dict = {
        "operation": "create",
        "instance": {"class": class_name, "data": instance},
    }
    if target_player_id:
        message["target_player_id"] = target_player_id
    return message


def destroy_websocket_message(
    class_name: str, instance_id, target_player_id: int | None = None
) -> dict:
    """
    Make a WebSocket message for communicating to the frontend that an instance has been destroyed.

    Args:
        class_name (str): The class name of the instance.
        instance_id (int): The ID of the instance.

    Returns:
        dict: The WebSocket message.
    """

    message: dict = {
        "operation": "destroy",
        "instance": {"class": class_name, "id": instance_id},
    }
    if target_player_id:
        message["target_player_id"] = target_player_id
    return message
