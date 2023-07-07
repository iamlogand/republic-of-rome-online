from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import FamilySenator
from rorapp.serializers import FamilySenatorSerializer


class FamilySenatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read senators.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FamilySenatorSerializer
    
    def get_queryset(self):
        # Optionally restricts the returned senators,
        # by filtering against a `game` query parameter in the URL.
        queryset = FamilySenator.objects.all()
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)
        return queryset
