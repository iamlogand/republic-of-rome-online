from django.contrib import admin
from rorapp.models import GameParticipant


# Admin configuration for game participants
@admin.register(GameParticipant)
class GameParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', "game", "join_date")
