from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rorapp.models import Game
from rorapp.serializers import GameSerializer


class GameViewSet(viewsets.ModelViewSet):

    queryset = Game.objects.select_related('host').all()
    permission_classes = [IsAuthenticated]
    serializer_class = GameSerializer

    def destroy(self, request, *args, **kwargs):
        """Ensure games can only be deleted by the host"""
        instance = self.get_object()
        if instance.host != request.user:
            return Response(
                {"error": "Only the host can delete their game."},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        """Ensure host is always request sender"""
        serializer.save(host=self.request.user)

    def perform_update(self, serializer):
        """Ensure host is always request sender"""
        serializer.save(host=self.request.user)
