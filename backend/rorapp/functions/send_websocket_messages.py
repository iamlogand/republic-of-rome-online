from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_websocket_messages(game_id, messages) -> None:
    '''
    Sends websocket messages to the game group.
    
    :return: None
    :rtype: None
    '''
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"game_{game_id}",
        {
            "type": "game_update",
            "messages": messages
        }
    )
