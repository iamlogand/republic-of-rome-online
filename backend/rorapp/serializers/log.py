from rest_framework import serializers

from rorapp.models import Log


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ["id", "game", "created_on", "text"]
