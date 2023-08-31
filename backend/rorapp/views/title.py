from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Title
from rorapp.serializers import TitleSerializer


class TitleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read titles.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TitleSerializer
    
    def get_queryset(self):
        queryset = Title.objects.all()
        
        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(senator__game__id=game_id)
            
        # Filter against an `active` query parameter in the URL
        # Active means that the title's end step is null
        active = self.request.query_params.get('active', None)
        if active is not None:
            queryset = queryset.filter(end_step__isnull=True)
            
        return queryset
