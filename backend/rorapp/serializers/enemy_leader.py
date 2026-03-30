from rest_framework import serializers

from rorapp.models import EnemyLeader


class EnemyLeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnemyLeader
        fields = [
            "id",
            "game",
            "name",
            "series_name",
            "strength",
            "disaster_number",
            "standoff_number",
            "active",
        ]
