from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from rorapp.game_state.send_game_state import send_game_state
from rorapp.models import Game
from rorapp.serializers import GameSerializer


class GameViewSet(viewsets.ModelViewSet):

    queryset = Game.objects.select_related("host").all()
    permission_classes = [IsAuthenticated]
    serializer_class = GameSerializer

    def get_queryset(self):
        if self.action in ["retrieve", "list"]:
            return (
                Game.objects.prefetch_related("factions").select_related("host").all()
            )
        else:
            return Game.objects.all()

    def validate_host(self, host):
        if host != self.request.user:
            raise PermissionDenied("You can only update or delete a game you host.")

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        self.validate_host(instance.host)
        serializer.save()
        send_game_state(instance.id)

    def perform_destroy(self, instance: Game):
        self.validate_host(instance.host)
        instance.delete()
