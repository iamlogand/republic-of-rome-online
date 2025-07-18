from rest_framework import serializers

from rorapp.models import Legion


class LegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legion
        fields = [
            "id",
            "game",
            "number",
            "veteran",
            "allegiance",
            "name",
            "strength",
            "campaign",
        ]
