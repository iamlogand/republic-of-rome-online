from datetime import datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Game
from rorapp.serializers import GameReadSerializer, GameWriteSerializer


class GameViewSet(viewsets.ModelViewSet):
    """
    Create and read games.
    """

    queryset = Game.objects.all()
    serializer_class = GameReadSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return GameWriteSerializer
        else:
            return GameReadSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Prefetch the owner's username to eliminate the need to make additional queries to the database
        return queryset.prefetch_related('owner')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
