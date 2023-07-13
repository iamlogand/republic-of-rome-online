from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rorapp.models import GameParticipant, Game
from rorapp.serializers import GameParticipantSerializer, GameParticipantCreateSerializer


class GameParticipantViewSet(viewsets.ModelViewSet):
    """
    Create, read and delete game participants.
    """

    serializer_class = GameParticipantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GameParticipantCreateSerializer
        else:
            return GameParticipantSerializer
    
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
        
        # Only allow if game has not started
        game = Game.objects.get(id=game_id)
        if game.step > 0:
            raise PermissionDenied('This game has already started.')
        
        # Only allow if no existing record has the same user and game
        existing_entry = GameParticipant.objects.filter(user__id=self.request.user.id, game__id=game_id)
        if existing_entry.exists():
            raise PermissionDenied('You have already joined this game.')
        
        # Only allow if less than 6 existing record have the same game
        existing_records = GameParticipant.objects.filter(game__id=game_id)
        if not existing_records.count() < 6:
            raise PermissionDenied('This game is full.')
        
        serializer.save(user=self.request.user)
        
    def perform_destroy(self, instance):
        game_id = instance.game.id
        
        # Only allow if game has not started
        game = Game.objects.get(id=game_id)
        if game.step > 0:
            raise PermissionDenied('This game has already started.')
        
        # Only allow if participant is the sender or sender is the host
        if instance.user.id != self.request.user.id and instance.game.host.id != self.request.user.id:
            raise PermissionDenied("Only the host can remove other participants from a game.")
        
        # Only allow if sender is not host
        if instance.game.host.id == instance.user.id:
            raise PermissionDenied("You can't leave your own game.")
        
        instance.delete()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')
    