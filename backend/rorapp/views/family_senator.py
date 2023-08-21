from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed
from rorapp.models import FamilySenator
from rorapp.serializers import FamilySenatorSerializer


class FamilySenatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read family senators.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FamilySenatorSerializer
    
    def get_queryset(self):
        queryset = FamilySenator.objects.all()
        
        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)
            
        return queryset
