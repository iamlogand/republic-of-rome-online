from rest_framework import viewsets
from django.contrib.auth.models import User
from rorapp.serializers import UserSerializer, UserDetailSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Get usernames of users or add a username to the URI to get the username and email of that user.
    """

    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            obj = self.get_object()
            if self.request.user == obj:
                return UserDetailSerializer
        return UserSerializer
