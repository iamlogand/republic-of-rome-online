from rest_framework import serializers

from rorapp.models import Province


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = [
            "id",
            "game",
            "name",
            "developed",
        ]
