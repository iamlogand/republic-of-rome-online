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
    lookup_field = 'username'
    
    def get_queryset(self):
        if 'username' in self.kwargs:
            if self.kwargs['username'] == self.request.user.username:
                return User.objects.filter(username=self.kwargs['username'])
            else:
                raise PermissionDenied("You do not have permission to access another user's details.")
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer
