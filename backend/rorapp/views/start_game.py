import json
import os
import random
from typing import List
from django.db import transaction
from django.conf import settings
from django.utils.timezone import now
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.send_game_state import send_game_state
from rorapp.models import Faction, Game, Log
from rorapp.models.senator import Senator


class StartGameViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def start_game(self, request, game_id: int) -> Response:

        # Validation
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            raise NotFound("Game not found")
        if request.user != game.host:
            raise PermissionDenied("Only the host can start the game")
        if game.status != "Pending":
            raise PermissionDenied("Game has already started")
        factions = Faction.objects.filter(game=game)
        if factions.count() < 3:
            raise PermissionDenied("Game must have at least 3 players to start")

        # Load senators from JSON data
        senator_json_path = os.path.join(
            settings.BASE_DIR, "rorapp", "data", "senator.json"
        )
        senators: List[Senator] = []
        with open(senator_json_path, "r") as file:
            senators_dict = json.load(file)
        for senator_name, senator_data in senators_dict.items():
            if senator_data["scenario"] == 1:
                senator = Senator(
                    name=senator_name,
                    game=game,
                    code=senator_data["code"],
                    military=senator_data["military"],
                    oratory=senator_data["oratory"],
                    loyalty=senator_data["loyalty"],
                    influence=senator_data["influence"],
                )
                senators.append(senator)

        # Select required number of senators
        random.shuffle(senators)
        senators = senators[: len(factions) * 3]

        # Assign temporary rome consul
        rome_consul = senators[0]
        rome_consul.add_title(Senator.Title.ROME_CONSUL)
        rome_consul.add_title(Senator.Title.HRAO)

        # Assign senators to factions
        random.shuffle(senators)
        senator_iterator = iter(senators)
        for faction in factions:
            for _ in range(3):
                senator = next(senator_iterator)
                senator.faction = faction
                senator.save()

        # Setup game
        game.step += 1
        game.started_on = now()
        game.state_treasury = 100
        game.phase = Game.Phase.INITIAL
        game.sub_phase = Game.SubPhase.FACTION_LEADER
        game.save()

        # Logging
        Log.create_object(
            game_id=game.id,
            text=f"The temporary Rome Consul is {rome_consul.display_name}.",
        )

        execute_effects_and_manage_actions(game.id)
        send_game_state(game.id)

        return Response({"message": "Game started"}, status=200)
