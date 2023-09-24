from django.db.models import Max
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import ActionLog
from rorapp.serializers import ActionLogSerializer


def normalize_index(index, queryset):

    # Convert index to integer
    try:
        index = int(index)
    except ValueError:
        return index
    
    # If index is negative then it's a reverse index,
    # so we convert it to the respective regular index
    if index < 0:
        last_index = queryset.aggregate(Max('index'))['index__max']
        if last_index is not None:
            index = last_index + index + 1
        
    return index


class ActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read action_logs.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ActionLogSerializer
    
    def get_queryset(self):
        queryset = ActionLog.objects.all()
        
        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(step__phase__turn__game__id=game_id)
        
        # Filter against a `min_index` query parameter in the URL
        min_index = self.request.query_params.get('min_index', None)
        if min_index is not None:
            queryset = queryset.filter(index__gte=normalize_index(min_index, queryset))
            
        # Filter against a `max_index` query parameter in the URL
        max_index = self.request.query_params.get('max_index', None)
        if max_index is not None:
            queryset = queryset.filter(index__lte=normalize_index(max_index, queryset))

        return queryset
