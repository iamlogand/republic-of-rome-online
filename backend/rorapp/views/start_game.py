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
from rest_framework.response import Response

from rorapp.models import Faction, Game
from rorapp.models.senator import Senator


class StartGameViewSet(viewsets.ViewSet):

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

        # Assign senators to factions
        random.shuffle(senators)
        senator_iterator = iter(senators)
        for faction in factions:
            for _ in range(3):
                senator = next(senator_iterator)
                senator.faction = faction
                senator.save()

        game.step += 1
        game.started_on = now()
        game.save()
        return Response({"message": "Game started"}, status=200)
