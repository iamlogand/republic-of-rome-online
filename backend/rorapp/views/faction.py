from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from rorapp.models import Faction
from rorapp.serializers import FactionPublicSerializer


class FactionViewSet(viewsets.ModelViewSet):

    queryset = Faction.objects.select_related("player").all()
    permission_classes = [IsAuthenticated]
    serializer_class = FactionPublicSerializer

    def validate_player(self, player):
        if player != self.request.user:
            raise PermissionDenied(
                "You can only update or delete a faction you control"
            )

    def validate_game(self, game):
        if game.status != "Pending":
            raise PermissionDenied(
                "You can only create, update or delete a faction before the game has started"
            )

    def validate_password(self, game):
        if (
            game.has_password
            and game.host_id != self.request.user.id
            and self.request.data.get("password") != game.password
        ):
            raise PermissionDenied("Invalid password")

    def perform_create(self, serializer):
        game = serializer.validated_data.get("game")
        self.validate_game(game)
        self.validate_password(game)
        serializer.save(player=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        self.validate_game(instance.game)
        self.validate_player(instance.player)

        # Prevent update of game field
        validated_data = serializer.validated_data
        validated_data.pop("game", None)

        serializer.save()

    def perform_destroy(self, instance):
        self.validate_game(instance.game)
        self.validate_player(instance.player)
        instance.delete()
