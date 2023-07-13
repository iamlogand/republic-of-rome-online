import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.game_group_name = "game_" + self.game_id

        # Join game group
        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )
        
        self.accept()

    def disconnect(self, close_code):
        # Leave game group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name, self.channel_name
        )
    
    # Handle game_message type message
    def game_message(self, event):
        # Echo the same message back to the client
        self.send(text_data=event["message"])
