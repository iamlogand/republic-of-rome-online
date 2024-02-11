from django.contrib import admin
from rorapp.models import War


# Admin configuration for wars
@admin.register(War)
class WarAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "name",
        "index",
        "game",
        "land_strength",
        "fleet_support",
        "naval_strength",
        "status",
        "undefeated_navy",
    )
