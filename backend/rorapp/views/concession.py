from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Concession
from rorapp.serializers import ConcessionSerializer


class ConcessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read concessions.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ConcessionSerializer

    def get_queryset(self):
        queryset = Concession.objects.all()

        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get("game", None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)

        return queryset
