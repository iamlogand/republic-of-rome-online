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

from rorapp.classes.concession import Concession
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.send_game_state import send_game_state
from rorapp.helpers.game_data import load_enemy_leaders, load_senators, load_statesmen
from rorapp.models import Faction, Game, Legion, Log, Senator, War


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
            raise PermissionDenied("Only the host can start the game.")
        if game.status != "pending":
            raise PermissionDenied("Game has already started.")
        factions = Faction.objects.filter(game=game)
        if factions.count() < 3:
            raise PermissionDenied("Game must have at least 3 players to start.")

        # Load senators from JSON data
        senators: List[Senator] = []
        senators_dict = load_senators()
        for senator_name, senator_data in senators_dict.items():
            if senator_data["scenario"] == 1:
                senator = Senator(
                    family_name=senator_name,
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
        all_senators_shuffled = senators.copy()
        senators = senators[: len(factions) * 3]

        # Assign temporary rome consul
        rome_consul = senators[0]
        rome_consul.add_title(Senator.Title.ROME_CONSUL)
        rome_consul.add_title(Senator.Title.HRAO)
        rome_consul.influence += 5

        # Assign senators to factions
        random.shuffle(senators)
        senator_iterator = iter(senators)
        for faction in factions:
            for _ in range(3):
                senator = next(senator_iterator)
                senator.faction = faction
                senator.save()

        # Build deck
        deck = []
        war_json_path = os.path.join(settings.BASE_DIR, "rorapp", "data", "war.json")
        with open(war_json_path, "r") as file:
            wars_dict = json.load(file)
        for key in wars_dict.keys():
            if key != "1st Punic War":
                deck.append("war:" + key)

        for concession in Concession:
            deck.append("concession:" + concession.value)

        for _ in range(7):
            deck.append("tribune")
        deck.append("assassin")
        deck.append("blackmail")
        deck.append("influence peddling")
        deck.append("secret bodyguard")
        deck.append("seduction")

        statesmen_dict = load_statesmen()
        for statesman_data in statesmen_dict.values():
            if statesman_data["scenario"] == 1:
                deck.append("statesman:" + statesman_data["code"])

        enemy_leaders_dict = load_enemy_leaders()
        for name in enemy_leaders_dict.keys():
            deck.append("leader:" + name)

        random.shuffle(deck)

        # Deal 3 faction cards to each faction
        # War and leader cards are skipped and shuffled back into the deck afterwards
        forum_discards = []
        for faction in factions:
            hand: list[str] = []
            while len(hand) < 3 and deck:
                card = deck.pop(0)
                if card.startswith("war:") or card.startswith("leader:"):
                    forum_discards.append(card)
                else:
                    hand.append(card)
            faction.cards = hand
            faction.save()
        deck.extend(forum_discards)
        for senator in all_senators_shuffled[len(factions) * 3 :]:
            deck.append("senator:" + str(senator.code))
        random.shuffle(deck)
        bottom = deck[-6:] + ["era ends"]
        random.shuffle(bottom)
        deck = deck[:-6] + bottom

        game.deck = deck

        # Setup game
        game.step += 1
        game.started_on = now()
        game.phase = Game.Phase.INITIAL
        game.sub_phase = Game.SubPhase.FACTION_LEADER
        game.save()

        # Create legions
        for num in range(1, 5):
            Legion.objects.create(game=game, number=num)

        # Create 1st Punic War
        for key, value in wars_dict.items():
            if key == "1st Punic War":
                war = War(
                    game=game,
                    name=key,
                    index=value["index"],
                    land_strength=value["land_strength"],
                    fleet_support=value["fleet_support"],
                    naval_strength=value["naval_strength"],
                    disaster_numbers=value["disaster_numbers"],
                    standoff_numbers=value["standoff_numbers"],
                    spoils=value["spoils"],
                    famine=value["famine"],
                    location=value["location"],
                    status=War.Status.INACTIVE,
                )
                if "series_name" in value:
                    war.series_name = value["series_name"]
                war.save()

        # Logging
        Log.create_object(
            game_id=game.id,
            text=f"The temporary Rome Consul is {rome_consul.display_name}.",
        )

        execute_effects_and_manage_actions(game.id)
        send_game_state(game.id)

        return Response({"message": "Game started"}, status=200)
