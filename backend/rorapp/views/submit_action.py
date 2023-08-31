from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rorapp.functions import select_faction_leader
from rorapp.models import Game, Faction, Step, PotentialAction

class SubmitActionViewSet(viewsets.ViewSet):
    '''
    Submit an action to delete a potential action and create a completed action.
    '''
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def submit_action(self, request, game_id=None, potential_action_id=None):
        
        # Try to get the game
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({"message": "Game not found"}, status=404)
        
        # Check if the game has not started
        if Step.objects.filter(phase__turn__game__id=game.id).count() == 0:
            return Response({"message": "Game has not started"}, status=403)
        
        # Try to get the faction
        try:
            faction = Faction.objects.filter(game__id=game.id).get(player__user__id=request.user.id)
        except Faction.DoesNotExist:
            return Response({"message": "Faction not found"}, status=404)

        # Try to get the potential action
        try:
            potential_action = PotentialAction.objects.filter(faction__id=faction.id).get(id=potential_action_id)
        except PotentialAction.DoesNotExist:
            return Response({"message": "Potential action not found"}, status=404)

        # Try to get the step
        try:
            step = Step.objects.get(id=potential_action.step.id)
        except PotentialAction.DoesNotExist:
            return Response({"message": "Step not found"}, status=404)
        
        # Action-specific logic
        match potential_action.type:
            case "select_faction_leader":
                return select_faction_leader(game, faction, potential_action, step, request.data)
            case _:
                return Response({"message": f"Action type is invalid"}, status=400)
