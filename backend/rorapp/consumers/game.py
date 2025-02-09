import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logger.info("Game connection accepted")

    async def disconnect(self, _):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
