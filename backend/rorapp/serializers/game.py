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


class SimpleGameSerializer(serializers.ModelSerializer):
    """Only used for API requests"""

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
            "has_password",
            "status",
            "votes_pending",
        ]
        read_only_fields = [
            "created_on",
            "started_on",
            "finished_on",
            "has_password",
            "status",
            "votes_pending",
        ]


class HostGameSerializer(SimpleGameSerializer):
    """Only used for API requests from the host"""

    class Meta(SimpleGameSerializer.Meta):
        fields = SimpleGameSerializer.Meta.fields + ["password"]
        read_only_fields = SimpleGameSerializer.Meta.read_only_fields


class GameSerializer(serializers.ModelSerializer):
    """Only used for WebSocket messages"""

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
            "has_password",
            "step",
            "turn",
            "phase",
            "sub_phase",
            "state_treasury",
            "unrest",
            "current_proposal",
            "votes_nay",
            "votes_yea",
            "defeated_proposals",
            "status",
            "votes_pending",
        ]
        read_only_fields = [
            "created_on",
            "started_on",
            "finished_on",
            "has_password",
            "step",
            "turn",
            "phase",
            "sub_phase",
            "state_treasury",
            "unrest",
            "current_proposal",
            "votes_nay",
            "votes_yea",
            "defeated_proposals",
            "status",
            "votes_pending",
        ]
