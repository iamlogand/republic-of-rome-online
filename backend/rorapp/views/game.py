from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from rorapp.models import Game
from rorapp.serializers import GameReadSerializer, GameCreateSerializer, GameUpdateSerializer


class GameViewSet(viewsets.ModelViewSet):
    """
    Create, read, partial update and delete games.
    """

    queryset = Game.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return GameCreateSerializer
        elif self.action == 'partial_update':
            return GameUpdateSerializer
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
    
    def perform_update(self, serializer):
        if serializer.instance.owner == self.request.user:
            return super().perform_update(serializer)
        else:
            raise PermissionDenied("You do not have permission to update this game.")
        
    def perform_destroy(self, instance):
        if instance.owner == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied("You do not have permission to delete this game.")
