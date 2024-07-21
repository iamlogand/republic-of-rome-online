from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Phase
from rorapp.serializers import PhaseSerializer


class PhaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read phases.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PhaseSerializer

    def get_queryset(self):
        queryset = Phase.objects.all()

        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get("game", None)
        if game_id is not None:
            queryset = queryset.filter(turn__game__id=game_id)

        # Ordering
        ordering = self.request.query_params.get("ordering", None)
        if ordering is not None:
            if ordering == "latest":
                queryset = queryset.order_by("-turn__index", "-index")
            else:
                queryset = queryset.order_by(ordering)

        # Limit
        limit = self.request.query_params.get("limit", None)
        if limit is not None:
            queryset = queryset[: int(limit)]

        return queryset
