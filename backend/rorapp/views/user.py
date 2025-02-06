from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rorapp.serializers import UserPublicSerializer, UserPrivateSerializer


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    # Creation via POST is disabled
    http_method_names = ["get", "head", "options", "put", "patch", "delete"]

    def get_serializer_class(self):
        if self.action == "retrieve" and self.request.user == self.get_object():
            return UserPrivateSerializer
        if self.action == "update" and self.request.user == self.get_object():
            return UserPrivateSerializer
        return UserPublicSerializer

    def destroy(self, request, *args, **kwargs):
        """Ensure that users can only delete their own account"""
        instance = self.get_object()
        if instance != request.user:
            return Response(
                {"error": "You can only delete your own user account."},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
