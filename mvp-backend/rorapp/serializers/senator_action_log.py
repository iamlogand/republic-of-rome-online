from rest_framework import serializers
from rorapp.models import SenatorActionLog


# Serializer used to read senator action logs
class SenatorActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SenatorActionLog
        fields = ("id", "senator", "action_log")
