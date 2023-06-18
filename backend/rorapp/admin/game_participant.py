from django.contrib import admin
from rorapp.models import GameParticipant

@admin.register(GameParticipant)
class GameParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', "game", "join_date")
