from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rorapp.functions import user_start_game


class StartGameViewSet(viewsets.ViewSet):
    """
    Start and setup an early republic scenario game.
    """

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def start_game(self, request, game_id=None):
        # This viewset method wraps the start_game function in a transaction
        return user_start_game(game_id, request.user)
