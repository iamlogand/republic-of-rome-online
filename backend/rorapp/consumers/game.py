import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.timezone import now
from rest_framework import serializers

from rorapp.game_state.get_game_state import get_public_game_state
from rorapp.models import Game, CombatCalculation, War, Senator
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
                        "public_game_state": public_game_state,
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
        serialized_data = CombatCalculationSerializer(queryset, many=True).data
        # Initial load - no transformations applied
        for item in serialized_data:
            item["auto_transformed"] = False
        return serialized_data

    def apply_auto_transformations(self, item, original_calculation):
        """Apply automatic transformations to combat calculation data.
        Returns tuple of (item, was_transformed)."""
        was_transformed = False

        # Auto-set battle type based on war's naval strength
        war_id = item.get("war")
        if (
            war_id
            and original_calculation
            and war_id != original_calculation.war_id
        ):
            try:
                war = War.objects.get(id=war_id, game=self.game_id)
                new_land_battle = war.naval_strength == 0
                if item.get("land_battle") != new_land_battle:
                    item["land_battle"] = new_land_battle
                    was_transformed = True
            except War.DoesNotExist:
                pass

        # Auto-generate name based on priority: war > commander > legions > fleets > untitled
        name = "Untitled"
        if war_id:
            try:
                war = War.objects.get(id=war_id, game=self.game_id)
                name = war.name
            except War.DoesNotExist:
                pass
        elif item.get("commander"):
            try:
                commander = Senator.objects.get(id=item["commander"], game=self.game_id)
                name = commander.display_name
            except Senator.DoesNotExist:
                pass
        elif (item.get("regular_legions", 0) + item.get("veteran_legions", 0)) > 0:
            name = "Legions"
        elif item.get("fleets", 0) > 0:
            name = "Fleets"

        if item.get("name") != name:
            item["name"] = name
            was_transformed = True

        return item, was_transformed

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
        transformed_ids = set()
        errors = []

        for item in data:
            calculation_id = item.get("id")
            original_calculation = None
            if calculation_id:
                try:
                    original_calculation = CombatCalculation.objects.get(
                        id=item.get("id")
                    )
                except CombatCalculation.DoesNotExist:
                    pass

            item, was_transformed = self.apply_auto_transformations(
                item, original_calculation
            )

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
                    if was_transformed:
                        transformed_ids.add(updated_instance.id)
                else:
                    errors.append({"id": instance_id, "errors": serializer.errors})
            else:
                # Create new instance
                item["game"] = self.game_id
                serializer = CombatCalculationSerializer(data=item)
                if serializer.is_valid():
                    new_instance = serializer.save()
                    updated_instances.append(new_instance)
                    if was_transformed:
                        transformed_ids.add(new_instance.id)
                else:
                    errors.append({"id": None, "errors": serializer.errors})

        if errors:
            raise serializers.ValidationError(errors)

        # Serialize and add auto_transformed flag
        serialized_data = CombatCalculationSerializer(updated_instances, many=True).data
        for item in serialized_data:
            item["auto_transformed"] = item["id"] in transformed_ids

        return serialized_data
