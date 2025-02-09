from django.contrib import admin

from rorapp.models import Faction


@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "player", "position")
