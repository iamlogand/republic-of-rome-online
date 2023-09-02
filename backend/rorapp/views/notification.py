from django.db.models import Max
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Notification
from rorapp.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read notifications.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        queryset = Notification.objects.all()
        
        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(step__phase__turn__game__id=game_id)
            
        # If the `latest` URL parameter is provided, return the highest index instance
        latest = self.request.query_params.get('latest', None)
        if latest is not None:
            max_index = queryset.aggregate(Max('index'))['index__max']
            return queryset.filter(index=max_index)
        
        # Filter against a `minIndex` query parameter in the URL
        min_index = self.request.query_params.get('minIndex', None)
        if min_index is not None:
            queryset = queryset.filter(index__gte=min_index)
            
        # Filter against a `maxIndex` query parameter in the URL
        max_index = self.request.query_params.get('maxIndex', None)
        if max_index is not None:
            queryset = queryset.filter(index__lte=max_index)

        return queryset
