from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Office
from rorapp.serializers import OfficeSerializer


class OfficeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read offices.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OfficeSerializer
    
    def get_queryset(self):
        # Optionally restricts the returned offices,
        # by filtering against a `game` query parameter in the URL.
        queryset = Office.objects.all()
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(senator__game__id=game_id)
        return queryset
