from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.functions.progress_helper import get_step
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

        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get("game", None)
        if game_id is not None:
            queryset = queryset.filter(step__phase__turn__game__id=game_id)

            # Filter against a `latest` query parameter in the URL
            latest = self.request.query_params.get("latest", None)
            if latest is not None:
                latest_step = get_step(game_id)
                if latest_step is not None:
                    queryset = queryset.filter(step__id=latest_step.id)

        return queryset
