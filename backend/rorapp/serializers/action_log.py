from rest_framework import serializers
from rorapp.models import ActionLog


# Serializer used to read action_logs
class ActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionLog
        fields = ("id", "index", "step", "type", "faction", "data", "creation_date")
