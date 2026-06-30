from rest_framework import serializers

from rorapp.helpers.provinces import get_province_definition
from rorapp.models import Province


class ProvinceSerializer(serializers.ModelSerializer):
    frontier = serializers.SerializerMethodField()
    in_forum = serializers.SerializerMethodField()

    class Meta:
        model = Province
        fields = [
            "id",
            "game",
            "name",
            "developed",
            "frontier",
            "in_forum",
        ]

    def get_frontier(self, province: Province) -> bool:
        return get_province_definition(province.name).get("frontier", False)

    def get_in_forum(self, province: Province) -> bool:
        return getattr(province, "governor_id", None) is None
