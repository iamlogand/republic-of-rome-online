import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings


class DebugConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not settings.TEST_ENDPOINTS_ENABLED:
            await self.close()
            return

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.group_name = f"debug_{self.game_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        state = await sync_to_async(self._get_resolver_state)()
        await self.send(text_data=json.dumps({"resolver": state}))

    async def disconnect(self, _):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def debug_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    def _get_resolver_state(self):
        from rorapp.views.test_helpers import _get_resolver_state, _resolver_cache_key

        return _get_resolver_state(_resolver_cache_key(self.game_id))
