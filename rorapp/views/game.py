from rest_framework.generics import ListAPIView
from rorapp.models import Game
from rorapp.serializers import GameSerializer

class GameView(ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer