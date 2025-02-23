from rest_framework import serializers

from rorapp.models import Log


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ["id", "game", "turn", "phase", "created_on", "text"]
