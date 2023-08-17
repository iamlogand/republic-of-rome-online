import os
import json
import random
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rorapp.models import Game, GameParticipant, Faction, FamilySenator, Office, Turn, Phase, Step
from rorapp.serializers import GameDetailSerializer, TurnSerializer, PhaseSerializer, StepSerializer


class StartGameViewSet(viewsets.ViewSet):
    '''
    Start and setup an early republic scenario game.
    '''
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def start_game(self, request, pk=None):
        
        # VALIDATION
        # Try to get the game
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response({"message": "Game not found"}, status=404)
        
        # Check if the user is not the game host
        if game.host.id != request.user.id:
            return Response({"message": "Only the host can start the game"}, status=403)
        
        # Check if the game has already started
        if Step.objects.filter(phase__turn__game__id=game.id).count() > 0:
            return Response({"message": "Game has already started"}, status=403)
        
        # Check if the game has less than 3 players
        participants = GameParticipant.objects.filter(game__id=game.id)
        if participants.count() < 3:
            return Response({"message": "Game must have at least 3 players to start"}, status=403)
        
        # ACTION
        # Create and save factions
        factions = []
        position = 1
        for participant in participants.order_by('?'):
            faction = Faction(game=game, position=position, player=participant)
            faction.save()  # Save factions to DB
            factions.append(faction)
            position += 1
            
        # Read family senator data
        senator_json_path = os.path.join(settings.BASE_DIR, 'rorapp', 'presets', 'family.json')
        with open(senator_json_path, 'r') as file:
            senators_dict = json.load(file)
        
        # Build a list of senators
        senators = []
        for senator_name, senator_data in senators_dict.items():
            if senator_data['scenario'] == 1:
                senator = FamilySenator(name=senator_name, game=game)
                senators.append(senator)
        
        # Shuffle the list
        required_senator_count = len(factions) * 3
        random.shuffle(senators)
        
        # Discard some, leaving only the required number of senators
        senators = senators[:required_senator_count]
        
        # Assign senators to factions
        senator_iterator = iter(senators)
        for faction in factions:
            for _ in range(3):
                senator = next(senator_iterator)
                senator.faction = faction
                senator.save()  # Save senators to DB
                
        # Assign temporary rome consul
        random.shuffle(senators)
        temp_rome_consul = Office(name="Temporary Rome Consul", senator=senators[0], start_step=1)
        temp_rome_consul.save()
        
        # Start the game
        game.start_date = timezone.now()
        game.save()  # Update game to DB
        
        # Create turn, phase and step
        turn = Turn(index=1, game=game)
        turn.save()
        phase = Phase(name="Mortality", turn=turn)
        phase.save()
        step = Step(index=1, phase=phase)
        step.save()
        
        # Send WebSocket messages
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"game_{game.id}",
            {
                "type": "game_update",
                "messages": [
                    {
                        "operation": "update",
                        "instance": {
                            "class": "game",
                            "data": GameDetailSerializer(game).data
                        }
                    },
                    {
                        "operation": "create",
                        "instance": {
                            "class": "turn",
                            "data": TurnSerializer(turn).data
                        }
                    },
                    {
                        "operation": "create",
                        "instance": {
                            "class": "phase",
                            "data": PhaseSerializer(phase).data
                        }
                    },
                    {
                        "operation": "create",
                        "instance": {
                            "class": "step",
                            "data": StepSerializer(step).data
                        }
                    }
                ]
            }
        )
        
        return Response({"message": "Game started successfully"}, status=200)
