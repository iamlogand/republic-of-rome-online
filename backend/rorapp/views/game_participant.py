from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rorapp.models import GameParticipant
from rorapp.serializers import GameParticipantSerializer


class GameParticipantViewSet(viewsets.ModelViewSet):
    """
    Create, read and delete game participants.
    """

    serializer_class = GameParticipantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Optionally restricts the returned game participants,
        # by filtering against a `game` query parameter in the URL.
        queryset = GameParticipant.objects.all()
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)
        return queryset
    
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
        
    def perform_destroy(self, instance):
        if instance.user.id != self.request.user.id and instance.game.host.id != self.request.user.id:
            # Stop deletion if player is not the request sender and the sender is not hosting the player
            raise PermissionDenied("You can't remove other participants from a game.")
        elif instance.game.host.id == instance.user.id:
            raise PermissionDenied("You can't leave your own game.")
        else:
            instance.delete()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')
    