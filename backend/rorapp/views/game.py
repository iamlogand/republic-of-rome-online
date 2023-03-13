from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Game
from rorapp.serializers import GameSerializer


class GameViewSet(viewsets.ModelViewSet):
    """
    Retrieve all games.
    """

    queryset = Game.objects.all().order_by('-creation_date')
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Prefetch the owner's username to eliminate the need to make additional queries to the database
        return queryset.prefetch_related('owner')
