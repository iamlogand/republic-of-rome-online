from typing import Type
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rorapp.actions.meta.action_manager import manage_actions
from rorapp.actions.meta.registry import action_registry
from rorapp.actions.meta.action_base import ActionBase
from rorapp.effects.meta.effect_executor import execute_effects
from rorapp.models import AvailableAction, Faction, Game


class SubmitActionViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def submit_action(self, request, game_id: int, action_name: str) -> Response:

        # Validation
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            raise NotFound("Game not found")
        try:
            faction = Faction.objects.get(game=game, player=request.user)
        except Faction.DoesNotExist:
            raise NotFound("Faction not found")
        try:
            available_action = AvailableAction.objects.get(
                game=game, faction=faction, name=action_name
            )
        except AvailableAction.DoesNotExist:
            raise NotFound("Available action not found")

        # Execute action
        action_cls: Type[ActionBase] = action_registry[available_action.name]
        action = action_cls()
        action.execute(game.id, faction.id, request.data)

        # Post execution jobs
        execute_effects(game.id)
        game.increment_step()

        return Response({"message": "Nice"}, status=200)
