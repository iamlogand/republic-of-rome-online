from rest_framework import serializers
from rorapp.models import Secret


# Serializer used by secret holders to read secrets
class SecretPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secret
        fields = ("id", "name", "type", "faction")


# Serializer used by anyone to read secrets
class SecretPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secret
        fields = ("id", "faction")  # `name` and `type` are hidden
