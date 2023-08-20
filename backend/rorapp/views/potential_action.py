from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import PotentialAction
from rorapp.serializers import PotentialActionSerializer


class PotentialActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read potential action.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PotentialActionSerializer
    
    def get_queryset(self):
        queryset = PotentialAction.objects.all()
        
        # Filter against a `step` query parameter in the URL
        step_id = self.request.query_params.get('step', None)
        if step_id is not None:
            queryset = queryset.filter(step__id=step_id)   
        
        return queryset
