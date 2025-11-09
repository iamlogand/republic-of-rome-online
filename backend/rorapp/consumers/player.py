import json
from asgiref.sync import sync_to_async
from django.utils.timezone import now
from channels.generic.websocket import AsyncWebsocketConsumer

from rorapp.game_state.get_game_state import get_private_game_state
from rorapp.models import Faction


class PlayerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_authenticated:
            game_id = self.scope["url_route"]["kwargs"]["game_id"]

            self.group_name = f"game_{game_id}_user_{user.id}"

            faction = None
            try:
                faction = await sync_to_async(Faction.objects.get)(
                    game=int(game_id), player=user.id
                )
            except:
                await self.close()
                return

            if faction:
                await self.accept()
                private_game_state = await sync_to_async(get_private_game_state)(
                    game_id, user.id
                )
                timestamp = (
                    now().isoformat(timespec="milliseconds").replace("+00:00", "Z")
                )
                await self.send(
                    text_data=json.dumps(
                        {
                            "private_game_state": private_game_state,
                            "timestamp": timestamp,
                        }
                    )
                )

                await self.channel_layer.group_add(self.group_name, self.channel_name)

        else:
            await self.close()

    async def disconnect(self, _):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_game_state(self, event):
        await self.send(text_data=event["message"])
