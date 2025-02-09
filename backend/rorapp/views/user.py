from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from rorapp.serializers import UserPublicSerializer, UserPrivateSerializer


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    # Creation via POST is disabled
    http_method_names = ["get", "head", "options", "put", "patch", "delete"]

    def get_serializer_class(self):
        if (
            self.action in ["retrieve", "update"]
        ) and self.request.user == self.get_object():
            return UserPrivateSerializer
        return UserPublicSerializer

    def validate_instance(self, instance):
        if instance != self.request.user:
            raise PermissionDenied(
                "You can only update or delete your own user account."
            )

    def perform_update(self, serializer):
        instance = self.get_object()
        self.validate_instance(instance)
        serializer.save()

    def perform_destroy(self, instance):
        self.validate_instance(instance)
        instance.delete()
