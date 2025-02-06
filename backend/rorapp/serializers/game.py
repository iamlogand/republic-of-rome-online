from rest_framework import serializers
from rorapp.models import Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name", "host")
        read_only_fields = ("host",)
