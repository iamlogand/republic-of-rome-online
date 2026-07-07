from rest_framework import serializers

from rorapp.models import Province


class ProvinceSerializer(serializers.ModelSerializer):
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

    def get_in_forum(self, province: Province) -> bool:
        return getattr(province, "governor_id", None) is None
