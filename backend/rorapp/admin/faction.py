from django.contrib import admin
from rorapp.models import Faction, Senator


# Inline table showing related senators
class SenatorInline(admin.TabularInline):
    model = Senator
    extra = 0


# Admin configuration for factions
@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "position", "player")
    inlines = [SenatorInline]
