from typing import List
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_websocket_messages(game_id: int, messages: List[dict]) -> None:
    """
    Send websocket messages to the game group.
    """

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"game_{game_id}", {"type": "game_update", "messages": messages}
    )


def create_websocket_message(class_name: str, instance: object) -> dict:
    """
    Make a WebSocket message for communicating to the frontend that an instance has been created.

    Args:
        class_name (str): The class name of the instance.
        instance (object): The instance.

    Returns:
        dict: The WebSocket message.
    """

    return {"operation": "create", "instance": {"class": class_name, "data": instance}}


def update_websocket_message(class_name: str, instance: object) -> dict:
    """
    Make a WebSocket message for communicating to the frontend that an instance has been updated.

    Args:
        class_name (str): The class name of the instance.
        instance (object): The instance.

    Returns:
        dict: The WebSocket message.
    """

    return {"operation": "update", "instance": {"class": class_name, "data": instance}}


def destroy_websocket_message(class_name: str, instance_id) -> dict:
    """
    Make a WebSocket message for communicating to the frontend that an instance has been destroyed.

    Args:
        class_name (str): The class name of the instance.
        instance_id (int): The ID of the instance.

    Returns:
        dict: The WebSocket message.
    """

    return {
        "operation": "destroy",
        "instance": {"class": class_name, "id": instance_id},
    }
