from rest_framework import serializers

from rorapp.models import War


class WarSerializer(serializers.ModelSerializer):
    class Meta:
        model = War
        fields = [
            "id",
            "game",
            "name",
            "series_name",
            "index",
            "land_strength",
            "fleet_support",
            "naval_strength",
            "disaster_numbers",
            "standoff_numbers",
            "spoils",
            "famine",
            "location",
            "status",
            "undefeated_navy",
            "unprosecuted",
        ]
