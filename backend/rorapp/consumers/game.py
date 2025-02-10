import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from rorapp.game_state.get_game_state import get_public_game_state
from rorapp.models import Game


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_authenticated:
            game_id = self.scope["url_route"]["kwargs"]["game_id"]
            self.group_name = f"game_{game_id}"

            try:
                await sync_to_async(Game.objects.get)(id=int(game_id))
            except:
                await self.close()
                return

            await self.accept()
            public_game_state, _ = await sync_to_async(get_public_game_state)(game_id)
            await self.send(text_data=json.dumps(public_game_state))

            await self.channel_layer.group_add(self.group_name, self.channel_name)

        else:
            await self.close()

    async def disconnect(self, _):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_game_state(self, event):
        await self.send(text_data=event["message"])
