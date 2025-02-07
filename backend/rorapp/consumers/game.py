from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_authenticated:
            self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
            self.group_name = f"game_{self.game_id}"

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, _):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
