from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_websocket_messages(game_id, messages) -> None:
    """
    Sends websocket messages to the game group.
    """

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"game_{game_id}", {"type": "game_update", "messages": messages}
    )


def create_websocket_message(class_name, instance) -> dict:
    """
    Helper function for making a WebSocket message to create an instance.
    The message should be used to communicate with the frontend when an instance is created.
    """

    return {"operation": "create", "instance": {"class": class_name, "data": instance}}


def update_websocket_message(class_name, instance) -> dict:
    """
    Helper function for making a WebSocket message to update an instance.
    The message should be used to communicate with the frontend when an instance is updated.
    """

    return {"operation": "update", "instance": {"class": class_name, "data": instance}}


def destroy_websocket_message(class_name, instance_id) -> dict:
    """
    Helper function for making a WebSocket message to destroy an instance.
    The message should be used to communicate with the frontend when an instance is destroyed.
    """

    return {
        "operation": "destroy",
        "instance": {"class": class_name, "id": instance_id},
    }
