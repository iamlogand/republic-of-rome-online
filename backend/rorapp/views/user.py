from rest_framework import viewsets
from django.contrib.auth.models import User
from rorapp.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ViewSet):
    """
    Retrieve the usernames of users.
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
