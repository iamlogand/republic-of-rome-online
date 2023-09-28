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
from rorapp.functions import rank_senators_and_factions
from rorapp.models import Game, Player, Faction, Senator, Title, Turn, Phase, Step, PotentialAction, ActionLog, SenatorActionLog
from rorapp.serializers import GameDetailSerializer, TurnSerializer, PhaseSerializer, StepSerializer


class StartGameViewSet(viewsets.ViewSet):
    '''
    Start and setup an early republic scenario game.
    '''
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def start_game(self, request, game_id=None):
        
        # ENSURE THAT GAME CAN BE STARTED
        
        # Try to get the game
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({"message": "Game not found"}, status=404)
        
        # Check if the user is not the game host
        if game.host.id != request.user.id:
            return Response({"message": "Only the host can start the game"}, status=403)
        
        # Check if the game has already started
        if Step.objects.filter(phase__turn__game__id=game.id).count() > 0:
            return Response({"message": "Game has already started"}, status=403)
        
        # Check if the game has less than 3 players
        players = Player.objects.filter(game__id=game.id)
        if players.count() < 3:
            return Response({"message": "Game must have at least 3 players to start"}, status=403)
        
        # START AND SETUP THE GAME
        
        # Create and save factions
        factions = []
        position = 1
        for player in players.order_by('?'):
            faction = Faction(game=game, position=position, player=player)
            faction.save()  # Save factions to DB
            factions.append(faction)
            position += 1
            
        # Read senator data
        senator_json_path = os.path.join(settings.BASE_DIR, 'rorapp', 'presets', 'senator.json')
        with open(senator_json_path, 'r') as file:
            senators_dict = json.load(file)
        
        # Build a list of senators
        senators = []
        for senator_name, senator_data in senators_dict.items():
            if senator_data['scenario'] == 1:
                senator = Senator(
                    name=senator_name,
                    game=game,
                    code=senator_data['code'],
                    military=senator_data['military'],
                    oratory=senator_data['oratory'],
                    loyalty=senator_data['loyalty'],
                    influence=senator_data['influence']
                )
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
        
        # Start the game
        game.start_date = timezone.now()
        game.save()  # Update game to DB
        
        # Create turn, phase and step
        turn = Turn(index=1, game=game)
        turn.save()
        phase = Phase(name="Faction", index=0, turn=turn)
        phase.save()
        step = Step(index=0, phase=phase)
        step.save()
                
        # Assign temporary rome consul
        random.shuffle(senators)
        temp_rome_consul_title = Title(name="Temporary Rome Consul", senator=senators[0], start_step=step, major_office=True)
        temp_rome_consul_title.save()
        
        # Update senator ranks
        rank_senators_and_factions(game.id)
        
        action_log = ActionLog(
            index=0,
            step=step,
            type="temporary_rome_consul",
            faction=temp_rome_consul_title.senator.faction,
            data={"senator": temp_rome_consul_title.senator.id}
        )
        action_log.save()
        senator_action_log = SenatorActionLog(
            senator=temp_rome_consul_title.senator,
            action_log=action_log
        )
        senator_action_log.save()
        
        # Create potential actions
        for faction in factions:
            action = PotentialAction(
                step=step, faction=faction, type="select_faction_leader",
                required=True, parameters=None
            )
            action.save()
            
        # COMMUNICATE CHANGES TO PLAYERS AND SPECTATORS
        
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
        
        return Response({"message": "Game started"}, status=200)
