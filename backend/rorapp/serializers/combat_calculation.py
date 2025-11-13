from rest_framework import serializers

from rorapp.models import CombatCalculation


class CombatCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CombatCalculation
        fields = [
            "id",
            "game",
            "name",
            "commander",
            "war",
            "land_battle",
            "regular_legions",
            "veteran_legions",
            "fleets",
        ]
