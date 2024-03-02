import json
import logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from rorapp.models import Player


logger = logging.getLogger(__name__)


class PlayerConsumer(WebsocketConsumer):
    def connect(self):
        # Check if the user is authenticated
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser):
            self.close()
            logger.info("Player connection closed by unauthenticated user")
            return

        # Check if the player exists
        self.player_id = self.scope["url_route"]["kwargs"]["player_id"]
        try:
            player = Player.objects.get(id=self.player_id)
        except Player.DoesNotExist:
            self.close()
            logger.info("Player connection closed by unauthorized user")
            return

        # Check if the player matches the user
        if player.user != user:
            self.close()
            logger.info("Player connection closed by unauthorized user")
            return

        # Join player group
        self.player_group_name = "player_" + self.player_id
        async_to_sync(self.channel_layer.group_add)(
            self.player_group_name, self.channel_name
        )

        self.accept()
        logger.info("Player connection accepted")

    def disconnect(self, close_code):
        # Leave player group
        try:
            if self.player_group_name:
                async_to_sync(self.channel_layer.group_discard)(
                    self.player_group_name, self.channel_name
                )
        except AttributeError:
            pass

    # Handle player_update type message
    def player_update(self, event):
        # Echo the same message back to the client
        message_str = json.dumps(event["messages"])
        self.send(text_data=message_str)
