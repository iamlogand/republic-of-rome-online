from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rorapp.models import Game, GameParticipant, Step
from rorapp.serializers import GameSerializer, GameDetailSerializer, GameCreateSerializer, GameUpdateSerializer


class GameViewSet(viewsets.ModelViewSet):
    """
    Create, read, partial update and delete games.
    """

    queryset = Game.objects.all().order_by('-creation_date')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return GameCreateSerializer
        elif self.action == 'partial_update':
            return GameUpdateSerializer
        elif 'prefetch_user' in self.request.query_params:
            return GameDetailSerializer
        else:
            return GameSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Prefetch the host's username to eliminate the need to make additional queries to the database
        return queryset.prefetch_related('host')

    def perform_create(self, serializer):
        game = serializer.save(host=self.request.user)
        game_participant = GameParticipant(user=game.host, game=game)
        game_participant.save()
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            # Update (PUT) is not allowed, but partial update (PATCH) is allowed
            raise MethodNotAllowed('PUT')
        return super().update(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        
        # Get this game instance
        game = serializer.instance
        
        # Only allow if game has not started
        step = Step.objects.filter(phase__turn__game__id=game.id)
        if step.count() > 0:
            raise PermissionDenied('This game has already started.')
        
        # Only allow if sender is the host
        if game.host != self.request.user:
            raise PermissionDenied("You do not have permission to update this game.")
        
        # Update the game
        super().perform_update(serializer)
    
        # Send a WebSocket message
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"game_{game.id}",
            {
                "type": "game_update",
                "messages": [
                    {
                        "operation": "update",
                        "instance": {
                            "class": "game",
                            "data": GameSerializer(game).data
                        }
                    }
                ]
            },
        )
    
    def perform_destroy(self, instance):
        if instance.host == self.request.user:
            instance_id = instance.id
            instance.delete()
            
            # Send a WebSocket message
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"game_{instance_id}",
                {
                    "type": "game_update",
                    "messages": [
                        {
                            "operation": "destroy",
                            "instance": {
                                "class": "game",
                                "id": instance_id
                            }
                        }
                    ]
                },
            )
        else:
            raise PermissionDenied("You do not have permission to delete this game.")
