from django.contrib.auth.models import User
from rest_framework import serializers

from rorapp.models import Faction


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class FactionSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = Faction
        # Only the position can be updated
        fields = ["id", "game", "player", "position"]
