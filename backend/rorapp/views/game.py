from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rorapp.models import Game
from rorapp.serializers import GameSerializer
from rest_framework.response import Response
from rest_framework import status


class GameViewSet(viewsets.ModelViewSet):
    """
    Retrieve all games.
    """

    queryset = Game.objects.all().order_by('-creation_date')
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Prefetch the owner's username to eliminate the need to make additional queries to the database
        return queryset.prefetch_related('owner')

    def create(self, request, *args, **kwargs):
        serializer = GameSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
