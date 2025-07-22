from django.contrib import admin
from rorapp.models import CombatCalculation


@admin.register(CombatCalculation)
class CombatCalculationAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "game",
        "name",
        "commander",
        "war",
        "land_battle",
        "legions",
        "veteran_legions",
        "fleets",
    )
