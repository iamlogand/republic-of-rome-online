from rest_framework import serializers
from rorapp.models import Turn


# Serializer used to read turns
class TurnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turn
        fields = ("id", "index", "game")
