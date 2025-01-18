from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from rorapp.models import Game
from rorapp.serializers import GameSerializer


class GameViewSet(viewsets.ModelViewSet):

    queryset = Game.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GameSerializer
