from rest_framework import serializers
from rorapp.models import Faction


# Serializer used to read factions
class FactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faction
        fields = ("id", "game", "position", "player", "rank", "custom_name")


# Serializer used to update factions
class FactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faction
        fields = ("id", "game", "position", "player", "rank", "custom_name")
        read_only_fields = ("id", "game", "position", "player", "rank")
