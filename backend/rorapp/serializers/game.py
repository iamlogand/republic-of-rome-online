from django.contrib.auth.models import User
from rest_framework import serializers

from rorapp.models import Game


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class GameSerializer(serializers.ModelSerializer):
    host = HostSerializer(read_only=True)

    class Meta:
        model = Game
        # Only the name can be updated
        fields = ["id", "name", "host", "created_on"]
        read_only_fields = ["created_on"]
