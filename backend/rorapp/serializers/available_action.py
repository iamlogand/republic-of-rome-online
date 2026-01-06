from rest_framework import serializers

from rorapp.models import AvailableAction


class AvailableActionSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()

    class Meta:
        model = AvailableAction
        fields = ["id", "game", "faction", "base_name", "variant_name", "name", "position", "schema", "context", "identifier"]
