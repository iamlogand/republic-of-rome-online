from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Action
from rorapp.serializers import ActionSerializer


class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read actions.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ActionSerializer
    
    def get_queryset(self):
        queryset = Action.objects.all()
        
        # Filter against a `step` query parameter in the URL
        step_id = self.request.query_params.get('step', None)
        if step_id is not None:
            queryset = queryset.filter(step__id=step_id)   
        
        return queryset
