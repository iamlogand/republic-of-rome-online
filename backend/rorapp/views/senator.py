from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed
from rorapp.models import Senator
from rorapp.serializers import SenatorSerializer


class SenatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read senators.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SenatorSerializer
    
    def get_queryset(self):
        queryset = Senator.objects.all()
        
        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)
            
        return queryset
