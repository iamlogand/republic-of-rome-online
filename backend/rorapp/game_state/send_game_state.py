import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rorapp.game_state.get_game_state import get_game_state


def send_game_state(game_id):
    game_state = get_game_state(game_id)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"game_{game_id}",
        {"type": "send_game_state", "message": json.dumps(game_state)},
    )
