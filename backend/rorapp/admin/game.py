from django.contrib import admin
from rorapp.models import Game, Player


# Inline table showing related game players
class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0


# Admin configuration for games
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("__str__", "host", "name", "creation_date", "start_date")
    search_fields = ("id", "host__username", "name")
    inlines = [PlayerInline]
