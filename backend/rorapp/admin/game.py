from django.contrib import admin
from rorapp.models import Game, GameParticipant


# Inline table showing related game participants
class GameParticipantInline(admin.TabularInline):
    model = GameParticipant
    extra = 0


# Admin configuration for games
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', "host", "creation_date", "start_date", 'step')
    inlines = [GameParticipantInline]
