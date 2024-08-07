from django.contrib import admin
from rorapp.models import Player


# Admin configuration for game players
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "game", "join_date")
