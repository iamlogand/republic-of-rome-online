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
        # Optionally restricts the returned family senators,
        # by filtering against a `game` query parameter in the URL.
        queryset = FamilySenator.objects.all()
        game_id = self.request.query_params.get('game', None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')
