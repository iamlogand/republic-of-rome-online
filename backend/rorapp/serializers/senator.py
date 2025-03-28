from rest_framework import serializers

from rorapp.models import Senator


class SenatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Senator
        fields = [
            "id",
            "game",
            "name",
            "code",
            "faction",
            "alive",
            "military",
            "oratory",
            "loyalty",
            "influence",
            "popularity",
            "knights",
            "talents",
            "votes",
            "status_items",
            "titles",
            "display_name",
        ]
