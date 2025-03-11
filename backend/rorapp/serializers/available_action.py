from rest_framework import serializers

from rorapp.models import AvailableAction


class AvailableActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableAction
        fields = ["id", "game", "faction", "name", "position", "schema", "context"]
