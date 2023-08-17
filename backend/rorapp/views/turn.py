from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Turn
from rorapp.serializers import TurnSerializer


class TurnViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read turns.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TurnSerializer
    
    def get_queryset(self):
        # Optionally restricts the returned turns,
        # by filtering against a `game` query parameter in the URL.
        queryset = Turn.objects.all()
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)
        return queryset
