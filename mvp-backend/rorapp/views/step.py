from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Step
from rorapp.serializers import StepSerializer


class StepViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read steps.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = StepSerializer

    def get_queryset(self):
        queryset = Step.objects.all()

        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get("game", None)
        if game_id is not None:
            queryset = queryset.filter(phase__turn__game__id=game_id)

        # Ordering
        ordering = self.request.query_params.get("ordering", None)
        if ordering is not None:
            queryset = queryset.order_by(ordering)

        # Limit
        limit = self.request.query_params.get("limit", None)
        if limit is not None:
            queryset = queryset[: int(limit)]

        return queryset
