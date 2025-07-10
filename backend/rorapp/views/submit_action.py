from typing import Type
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rorapp.actions.meta.registry import action_registry
from rorapp.actions.meta.action_base import ActionBase
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.send_game_state import send_game_state
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
        game_state = GameStateLive(game_id)
        if not action.is_allowed(game_state, faction.id):
            raise RuntimeError("Action not allowed")
        execution_result = action.execute(game.id, faction.id, request.data)
        if not execution_result.success:
            return Response(
                {"message": execution_result.message},
                status=400,
            )

        # Post execution jobs
        execute_effects_and_manage_actions(game_id)
        send_game_state(game.id)

        return Response({"message": "Action submitted"}, status=200)
