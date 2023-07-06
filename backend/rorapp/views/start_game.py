import os
import json
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rorapp.models import Game, GameParticipant, Faction, FamilySenator


class StartGameViewset(viewsets.ViewSet):
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def start_game(self, request, pk=None):
        
        # Try to get the game
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response({"message": "Game not found"}, status=404)
        
        # Check if the user is not the game host
        if game.host.id != request.user.id:
            return Response({"message": "Only the host can start the game"}, status=403)
        
        # Check if the game has already started
        if game.step != 0:
            return Response({"message": "Game has already started"}, status=403)
        
        # Check if the game has less than 3 players
        participants = GameParticipant.objects.filter(game__id=game.id)
        if participants.count() < 3:
            return Response({"message": "Game must have at least 3 players to start"}, status=403)
        
        # Create factions
        position = 1
        for participant in participants.order_by('?'):
            faction = Faction(game=game, position=position, player=participant)
            faction.save()
            position += 1
        
        # Build a deck of family senators
        senator_json_path = os.path.join(settings.BASE_DIR, 'rorapp', 'presets', 'family.json')
        with open(senator_json_path, 'r') as file:
            senators_json = json.load(file)
        for senator_name, senator_data in senators_json.items():
            senator = FamilySenator(name=senator_name, game=game)
            senator.save()
        
        # Draw senators
        senators = FamilySenator.objects.filter(game__exact=game.id)
        factions = Faction.objects.filter(game__exact=game)
        required_senator_count = factions.count() * 3
        drawn_senators = senators.order_by('?')[:required_senator_count]
        
        # Assign senators to factions
        senator_iterator = iter(drawn_senators)
        for faction in factions:
            for _ in range(3):
                senator = next(senator_iterator)
                senator.faction = faction
                senator.save()
        
        # Start the game
        game.start_date = timezone.now()
        game.step = 1
        game.save()
        return Response({"message": "Game started successfully"}, status=200)
