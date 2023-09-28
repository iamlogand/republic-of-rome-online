from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import SenatorActionLog
from rorapp.serializers import SenatorActionLogSerializer


class SenatorActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read senator action logs. Optionally accepts a `senator` URL parameter for filtering.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SenatorActionLogSerializer
    
    def get_queryset(self):
        queryset = SenatorActionLog.objects.all()
            
        # Filter against a `senator` query parameter in the URL
        senator_id = self.request.query_params.get('senator', None)
        if senator_id is not None:
            queryset = queryset.filter(senator__id=senator_id)

        return queryset
