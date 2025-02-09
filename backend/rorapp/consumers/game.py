import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from rorapp.game_state.game_state import get_game_state


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_authenticated:
            self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
            self.group_name = f"game_{self.game_id}"

            await self.accept()
            game_state = await sync_to_async(get_game_state)(self.game_id)
            await self.send(text_data=json.dumps(game_state))

            await self.channel_layer.group_add(self.group_name, self.channel_name)

        else:
            await self.close()

    async def disconnect(self, _):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
