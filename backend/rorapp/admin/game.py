from django.contrib import admin
from rorapp.models import Game, GameParticipant


class GameParticipantInline(admin.TabularInline):
    model = GameParticipant
    extra = 0
    
    
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', "owner", "creation_date", "start_date")
    inlines = [GameParticipantInline]
    