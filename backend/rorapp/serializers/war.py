from rest_framework import serializers
from rorapp.models import War


# Serializer used to read war
class WarSerializer(serializers.ModelSerializer):
    class Meta:
        model = War
        fields = (
            "name",
            "index",
            "game",
            "land_strength",
            "naval_support",
            "naval_strength",
            "disaster_numbers",
            "standoff_numbers",
            "spoils",
            "status",
            "naval_defeated",
            "famine",
        )
