import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rorapp.game_state.get_game_state import get_public_game_state, get_private_game_state


def send_game_state(game_id):
    public_game_state, player_ids = get_public_game_state(game_id)
        
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f"game_{game_id}",
        {"type": "send_game_state", "message": json.dumps(public_game_state)},
    )
    
    for player_id in player_ids:
        private_game_state = get_private_game_state(game_id, player_id)
        async_to_sync(channel_layer.group_send)(
            f"game_{game_id}_user_{player_id}",
            {"type": "send_game_state", "message": json.dumps(private_game_state)},
        )
