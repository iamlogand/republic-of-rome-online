from rest_framework import viewsets
from rorapp.models import Game
from rorapp.serializers import GameSerializer

class GameView(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    