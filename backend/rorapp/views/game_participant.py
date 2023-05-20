from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rorapp.models import GameParticipant
from rorapp.serializers import GameParticipantCreateSerializer


class GameParticipantViewSet(viewsets.ModelViewSet):
    """
    Read game participants. Other operations are not allowed.
    """

    queryset = GameParticipant.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return GameParticipantCreateSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Prefetch the owner's username to eliminate the need to make additional queries to the database
        return queryset.prefetch_related('user')
    
    def perform_create(self, serializer):
        game_id = self.request.data['game']
        
        # Only allow creation if no existing record has the same user and game
        existing_entry = GameParticipant.objects.filter(user__id=self.request.user.id, game__id=game_id)
        if existing_entry.exists():
            raise PermissionDenied('You have already joined this game.')
        
        # Only allow creation if less than 6 existing record have the same game
        existing_records = GameParticipant.objects.filter(game__id=game_id)
        if not existing_records.count() < 6:
            raise PermissionDenied('This game is full.')
        
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')
    