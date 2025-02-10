from django.contrib.auth.models import User
from rest_framework import serializers

from rorapp.models import Faction


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class FactionPublicSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = Faction
        fields = ["id", "game", "player", "position", "card_count"]
        read_only_fields = ["card_count"]


class FactionPrivateSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = Faction
        fields = ["id", "game", "player", "position", "treasury", "cards", "card_count"]
