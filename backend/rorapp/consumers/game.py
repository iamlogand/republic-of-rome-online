import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class GameConsumer(WebsocketConsumer):
    def connect(self):
        # Log the cookies
        print(f"Consumer cookies: {self.scope.get('headers')}")
        
        user = self.scope.get('user')
        print(f"Consumer user: {user}")  # log user
        if user and not isinstance(user, AnonymousUser):
            self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
            self.game_group_name = "game_" + self.game_id

            # Join game group
            async_to_sync(self.channel_layer.group_add)(
                self.game_group_name, self.channel_name
            )
            
            self.accept()
            print("Connection accepted")  # log connection status
        else:
            self.close()
            print("Connection closed")  # log connection status

    def disconnect(self, close_code):
        # Leave game group
        try:
            if self.game_group_name:
                async_to_sync(self.channel_layer.group_discard)(
                    self.game_group_name, self.channel_name
                )
        except AttributeError:
            pass
    
    # Handle game_update type message
    def game_update(self, event):
        # Echo the same message back to the client
        message_str = json.dumps(event["messages"])
        self.send(text_data=message_str)
