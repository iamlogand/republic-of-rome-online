from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rorapp.functions.face_mortality import face_mortality
from rorapp.functions.select_faction_leader import select_faction_leader
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
        if Step.objects.filter(phase__turn__game=game.id).count() == 0:
            return Response({"message": "Game has not started"}, status=403)
        
        # Try to get the faction
        try:
            faction = Faction.objects.filter(game=game.id).get(player__user=request.user.id)
        except Faction.DoesNotExist:
            return Response({"message": "You must control a faction in this game to take actions"}, status=403)

        # Try to get the potential action
        try:
            potential_action = PotentialAction.objects.filter(faction=faction.id).get(id=potential_action_id)
        except PotentialAction.DoesNotExist:
            return Response({"message": "Potential action not found"}, status=404)

        # Get the step and ensure that it's the current step
        step = Step.objects.get(id=potential_action.step.id)
        latest_step = Step.objects.filter(phase__turn__game=game).order_by('-index')[0]
        if step.index != latest_step.index:
            return Response({"message": "Potential action is not related to the current step"}, status=403)
        
        # Action-specific logic
        match potential_action.type:
            case "select_faction_leader":
                return select_faction_leader(game, faction, potential_action, step, request.data)
            case "face_mortality":
                return face_mortality(game, faction, potential_action, step)
            case _:
                return Response({"message": f"Action type is invalid"}, status=400)
