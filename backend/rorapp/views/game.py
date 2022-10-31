from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Game
from rorapp.serializers import GameSerializer

class GameView(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by('name')
    serializer_class = GameSerializer

    # permission_classes = [IsAuthenticated]