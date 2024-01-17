from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Secret
from rorapp.serializers import SecretPrivateSerializer, SecretPublicSerializer


class SecretPrivateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read secrets that belong to the requesting player's faction.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SecretPrivateSerializer

    def get_queryset(self):
        queryset = Secret.objects.filter(faction__player__user=self.request.user)

        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get("game", None)
        if game_id is not None:
            queryset = queryset.filter(faction__game__id=game_id)

        return queryset


class SecretPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read secrets that don't belong to the requesting player's faction.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SecretPublicSerializer

    def get_queryset(self):
        queryset = Secret.objects.exclude(faction__player__user=self.request.user)

        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get("game", None)
        if game_id is not None:
            queryset = queryset.filter(faction__game__id=game_id)

        return queryset
