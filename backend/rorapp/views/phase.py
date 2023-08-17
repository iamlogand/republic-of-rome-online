from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Phase
from rorapp.serializers import PhaseSerializer


class PhaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read phases.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PhaseSerializer
    
    def get_queryset(self):
        # Optionally restricts the returned turns,
        # by filtering against a `game` query parameter in the URL.
        queryset = Phase.objects.all()
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(turn__game__id=game_id)
        return queryset
