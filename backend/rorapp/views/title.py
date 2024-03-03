from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Title
from rorapp.serializers import TitleSerializer


class TitleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read titles. Optionally accepts a `relevant` URL parameter for filtering.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TitleSerializer
    
    def get_queryset(self):
        queryset = Title.objects.all()
        
        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(senator__game__id=game_id)
            
        # Filter against an `relevant` query parameter in the URL
        # Active means that the title's end step is null or the senator is dead
        active = self.request.query_params.get('relevant', None)
        if active is not None:
            queryset = queryset.filter(Q(end_step__isnull=True) | Q(senator__alive=False))
            
        return queryset
