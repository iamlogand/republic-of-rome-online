import asyncio
import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import now
from rest_framework import serializers

from rorapp.game_state.get_game_state import get_public_game_state
from rorapp.models import Game, CombatCalculation
from rorapp.serializers import CombatCalculationSerializer


class GameConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending_updates = []
        self.broadcast_task = None

    async def connect(self):
        user = self.scope["user"]

        if user.is_authenticated:
            self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
            self.group_name = f"game_{self.game_id}"

            try:
                await sync_to_async(Game.objects.get)(id=int(self.game_id))
                public_game_state, _ = await sync_to_async(get_public_game_state)(
                    self.game_id
                )
                calculations = await self.get_current_calculations()
            except:
                await self.close()
                return

            await self.accept()
            
            timestamp = now().isoformat(timespec="milliseconds").replace("+00:00", "Z")
            await self.send(
                text_data=json.dumps(
                    {
                        "game_state": public_game_state,
                        "combat_calculations": calculations,
                        "timestamp": timestamp,
                    }
                )
            )
            await self.channel_layer.group_add(self.group_name, self.channel_name)

        else:
            await self.close()

    async def disconnect(self, _):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, data):
        if "combat_calculations" in data:
            await self.handle_combat_calculations(data)
        else:
            pass

    async def handle_combat_calculations(self, data):
        incoming_data = data.get("combat_calculations", [])
        timestamp = data.get("timestamp", "")
        calculations = await self.update_calculations(incoming_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast_combat_calculations",
                "data": {
                    "combat_calculations": calculations,
                    "timestamp": timestamp,
                },
            },
        )

    async def broadcast_combat_calculations(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def send_game_state(self, event):
        await self.send(text_data=event["message"])

    @database_sync_to_async
    def get_current_calculations(self):
        queryset = CombatCalculation.objects.filter(game=self.game_id)
        return CombatCalculationSerializer(queryset, many=True).data

    @database_sync_to_async
    def update_calculations(self, data):
        incoming_ids = {item.get("id") for item in data if item.get("id") is not None}

        existing_calculations = CombatCalculation.objects.filter(game=self.game_id)
        existing_ids = {calc.id for calc in existing_calculations}

        ids_to_delete = existing_ids - incoming_ids
        if ids_to_delete:
            CombatCalculation.objects.filter(id__in=ids_to_delete).delete()

        instance_mapping = {
            inst.id: inst for inst in existing_calculations if inst.id in incoming_ids
        }

        updated_instances = []
        errors = []

        for item in data:
            instance_id = item.get("id")
            if instance_id:
                # Update existing instance
                instance = instance_mapping.get(instance_id)
                if not instance:
                    errors.append(
                        {
                            "id": instance_id,
                            "error": "Instance not found or invalid game",
                        }
                    )
                    continue

                serializer = CombatCalculationSerializer(
                    instance, data=item, partial=True
                )
                if serializer.is_valid():
                    updated_instance = serializer.save()
                    updated_instances.append(updated_instance)
                else:
                    errors.append({"id": instance_id, "errors": serializer.errors})
            else:
                # Create new instance
                item["game"] = self.game_id
                serializer = CombatCalculationSerializer(data=item)
                if serializer.is_valid():
                    new_instance = serializer.save()
                    updated_instances.append(new_instance)
                else:
                    errors.append({"id": None, "errors": serializer.errors})

        if errors:
            raise serializers.ValidationError(errors)

        return CombatCalculationSerializer(updated_instances, many=True).data
