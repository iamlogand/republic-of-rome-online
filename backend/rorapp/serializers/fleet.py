from rest_framework import serializers

from rorapp.models import Fleet


class FleetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fleet
        fields = [
            "id",
            "game",
            "number",
            "name",
        ]
