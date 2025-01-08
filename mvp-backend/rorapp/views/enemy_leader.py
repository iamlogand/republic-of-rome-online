from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import EnemyLeader
from rorapp.serializers import EnemyLeaderSerializer


class EnemyLeaderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read enemy leaders.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = EnemyLeaderSerializer

    def get_queryset(self):
        queryset = EnemyLeader.objects.all()

        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get("game", None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)

        return queryset
