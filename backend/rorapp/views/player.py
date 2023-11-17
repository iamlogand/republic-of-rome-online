from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rorapp.functions import (
    send_websocket_messages,
    create_websocket_message,
    destroy_websocket_message,
)
from rorapp.models import Player, Game, Step
from rorapp.serializers import (
    PlayerSerializer,
    PlayerDetailSerializer,
    PlayerCreateSerializer,
)


class PlayerViewSet(viewsets.ModelViewSet):
    """
    Create, read and delete game players. Optionally accepts a `prefetch_user` URL parameter.
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return PlayerCreateSerializer
        elif "prefetch_user" in self.request.query_params:
            return PlayerDetailSerializer
        else:
            return PlayerSerializer

    def get_queryset(self):
        queryset = Player.objects.all()

        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get("game", None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        game_id = self.request.data["game"]

        # Only allow if game has not started
        game = Game.objects.get(id=game_id)
        step = Step.objects.filter(phase__turn__game__id=game.id)
        if step.count():
            raise PermissionDenied("This game has already started.")

        # Only allow if no existing record has the same user and game
        existing_entry = Player.objects.filter(
            user__id=self.request.user.id, game__id=game_id
        )
        if existing_entry.exists():
            raise PermissionDenied("You have already joined this game.")

        # Only allow if less than 6 existing record have the same game
        existing_records = Player.objects.filter(game__id=game_id)
        if not existing_records.count() < 6:
            raise PermissionDenied("This game is full.")

        # Create new instance
        instance = serializer.save(user=self.request.user)

        # Serialize the instance
        instance_data = PlayerDetailSerializer(instance).data

        # Send a WebSocket message
        messages_to_send = [create_websocket_message("player", instance_data)]
        send_websocket_messages(game.id, messages_to_send)

    @transaction.atomic
    def perform_destroy(self, instance):
        game_id = instance.game.id

        # Only allow if game has not started
        game = Game.objects.get(id=game_id)
        step = Step.objects.filter(phase__turn__game__id=game.id)
        if step.count():
            raise PermissionDenied("This game has already started.")

        # Only allow if player is the sender or sender is the host
        if (
            instance.user.id != self.request.user.id
            and instance.game.host.id != self.request.user.id
        ):
            raise PermissionDenied(
                "Only the host can remove other players from a game."
            )

        # Only allow if sender is not host
        if instance.game.host.id == instance.user.id:
            raise PermissionDenied("You can't leave your own game.")

        instance_id = instance.id
        instance.delete()

        # Send a WebSocket message
        messages_to_send = [destroy_websocket_message("player", instance_id)]
        send_websocket_messages(game.id, messages_to_send)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH")
