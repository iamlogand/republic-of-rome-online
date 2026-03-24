from rest_framework import serializers

from rorapp.models import Senator


class SenatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Senator
        fields = [
            "id",
            "game",
            "family_name",
            "statesman_name",
            "family",
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
            "concessions",
            "corrupt_concessions",
            "location",
            "display_name",
        ]
