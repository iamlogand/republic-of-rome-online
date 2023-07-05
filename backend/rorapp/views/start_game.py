from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rorapp.models import Game, GameParticipant


class StartGameViewset(viewsets.ViewSet):
    
    @action(detail=True, methods=['post'])
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
        
        # Start the game
        game.start_date = timezone.now()
        game.step = 1
        game.save()
        return Response({"message": "Game started successfully"}, status=200)
