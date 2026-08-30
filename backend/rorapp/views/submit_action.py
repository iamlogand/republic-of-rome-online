from contextlib import nullcontext
from typing import Optional, Type

from django.conf import settings
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rorapp.actions.meta.registry import action_registry
from rorapp.actions.meta.action_base import ActionBase
from rorapp.classes.random_resolver import RandomResolver, RealRandomResolver
from rorapp.effects.meta.effect_executor import execute_effects_and_manage_actions
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.send_game_state import send_game_state
from rorapp.models import AvailableAction, Faction, Game
from rorapp.helpers.resolver_cache import fake_resolver_from_cache


class SubmitActionViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def submit_action(
        self,
        request,
        game_id: int,
        action_id: int,
        random_resolver: Optional[RandomResolver] = None,
    ) -> Response:

        # Validation
        try:
            # Lock the game row to ensure all actions for this game are processed sequentially
            game = Game.objects.select_for_update().get(id=game_id)
        except Game.DoesNotExist:
            raise NotFound("Game not found")
        try:
            faction = Faction.objects.get(game=game, player=request.user)
        except Faction.DoesNotExist:
            raise NotFound("Faction not found")
        try:
            available_action = AvailableAction.objects.get(
                id=action_id, game=game, faction=faction
            )
        except AvailableAction.DoesNotExist:
            raise NotFound("Available action not found")

        # Execute action
        # Use base_name for registry lookup
        action_cls: Type[ActionBase] = action_registry[available_action.base_name]
        action = action_cls()
        game_state = GameStateLive(game_id)
        if not action.is_allowed(game_state, faction.id):
            raise RuntimeError("Action not allowed")

        resolver_context = (
            fake_resolver_from_cache(game_id)
            if settings.TEST_ENDPOINTS_ENABLED
            else nullcontext(None)
        )
        with resolver_context as cached_resolver:
            if random_resolver is None:
                random_resolver = cached_resolver or RealRandomResolver()

            # Merge context into selection data so execute() can access it
            selection_data = dict(request.data)
            selection_data.update(available_action.context)

            execution_result = action.execute(
                game.id, faction.id, selection_data, random_resolver
            )
            if not execution_result.success:
                return Response(
                    {"message": execution_result.message},
                    status=400,
                )

            # Post execution jobs
            execute_effects_and_manage_actions(game_id, random_resolver)
            send_game_state(game.id)

        return Response({"message": "Action submitted"}, status=200)
