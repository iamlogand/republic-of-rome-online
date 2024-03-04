from rest_framework import serializers
from rorapp.models import Game
from rorapp.serializers.user import UserSerializer


# Serializer used to read and delete games
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = (
            "id",
            "name",
            "description",
            "creation_date",
            "start_date",
            "host",
            "end_date",
        )
        read_only_fields = [
            "id",
            "name",
            "description",
            "creation_date",
            "start_date",
            "host",
            "end_date",
        ]


# Serializer used to read games in detail and prefetch users
class GameDetailSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)

    class Meta:
        model = Game
        fields = (
            "id",
            "name",
            "description",
            "creation_date",
            "start_date",
            "host",
            "end_date",
        )
        read_only_fields = [
            "id",
            "name",
            "description",
            "creation_date",
            "start_date",
            "host",
            "end_date",
        ]


# Serializer used to create games
class GameCreateSerializer(serializers.ModelSerializer):
    host = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Game
        fields = ("id", "name", "description", "host")
        read_only_fields = ["id"]


# Serializer used to update games
class GameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "name", "description", "creation_date", "start_date", "host")
        read_only_fields = ["id", "name", "creation_date", "start_date", "host"]
