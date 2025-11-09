import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import now
from rorapp.game_state.get_game_state import get_public_game_state, get_private_game_state


def send_game_state(game_id):
    public_game_state, player_ids = get_public_game_state(game_id)
        
    channel_layer = get_channel_layer()
    
    timestamp = now().isoformat(timespec="milliseconds").replace("+00:00", "Z")
    public_message = {"public_game_state": public_game_state, "timestamp": timestamp}
    
    async_to_sync(channel_layer.group_send)(
        f"game_{game_id}",
        {"type": "send_game_state", "message": json.dumps(public_message)},
    )
    
    for player_id in player_ids:
        private_game_state = get_private_game_state(game_id, player_id)
        
        # Private game state has a simpler structure than public game state
        private_message = {"private_game_state": private_game_state, "timestamp": timestamp}
        async_to_sync(channel_layer.group_send)(
            f"game_{game_id}_user_{player_id}",
            {"type": "send_game_state", "message": json.dumps(private_message)},
        )
