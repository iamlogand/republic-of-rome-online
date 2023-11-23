from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rorapp.functions import face_mortality, select_faction_leader
from rorapp.models import Game, Faction, Step, Action


class SubmitActionViewSet(viewsets.ViewSet):
    """
    Submit an action to mark the action as complete and affect the game.
    """

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def submit_action(self, request, game_id, action_id=None):
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
            faction = Faction.objects.filter(game=game.id).get(
                player__user=request.user.id
            )
        except Faction.DoesNotExist:
            return Response(
                {"message": "You must control a faction in this game to take actions"},
                status=403,
            )

        # Try to get the action
        try:
            action = Action.objects.filter(faction=faction.id, completed=False).get(
                id=action_id
            )
        except Action.DoesNotExist:
            return Response({"message": "Action not found"}, status=404)

        # Get the step and ensure that it's the current step
        step = Step.objects.get(id=action.step.id)
        latest_step = Step.objects.filter(phase__turn__game=game).order_by("-index")[0]
        if step.index != latest_step.index:
            return Response(
                {"message": "Action is not related to the current step"}, status=403
            )

        # Action-specific logic
        match action.type:
            case "select_faction_leader":
                return select_faction_leader(action.id, request.data)
            case "face_mortality":
                return face_mortality(action.id)
            case _:
                return Response({"message": "Action type is invalid"}, status=400)
