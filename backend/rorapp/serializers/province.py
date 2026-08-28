from rest_framework import serializers

from rorapp.models import Province


class ProvinceSerializer(serializers.ModelSerializer):
    governor: serializers.PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Province
        fields = [
            "id",
            "game",
            "name",
            "developed",
            "frontier",
            "governor",
            "term",
            "elected_this_turn",
        ]