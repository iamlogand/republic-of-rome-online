from rest_framework import serializers
from rorapp.models import EnemyLeader


# Serializer used to read enemy leaders
class EnemyLeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnemyLeader
        fields = (
            "id",
            "name",
            "game",
            "strength",
            "disaster_number",
            "standoff_number",
            "war_name",
            "current_war",
            "dead",
        )
