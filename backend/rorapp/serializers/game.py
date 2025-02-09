from django.contrib.auth.models import User
from rest_framework import serializers

from rorapp.models import Faction, Game


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class FactionSerializer(serializers.ModelSerializer):
    player = UserSerializer(read_only=True)

    class Meta:
        model = Faction
        fields = ["player"]


class GameSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    factions = FactionSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            "id",
            "name",
            "host",
            "created_on",
            "started_on",
            "finished_on",
            "factions",
            "status",
        ]
        read_only_fields = ["created_on", "started_on", "finished_on", "status"]


class SimpleGameSerializer(serializers.ModelSerializer):
    """Should only be used for WebSocket messages"""

    host = UserSerializer(read_only=True)

    class Meta:
        model = Game
        fields = [
            "id",
            "name",
            "host",
            "created_on",
            "started_on",
            "finished_on",
            "status",
        ]
        read_only_fields = ["created_on", "started_on", "finished_on", "status"]
