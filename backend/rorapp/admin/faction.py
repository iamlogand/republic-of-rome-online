from django.contrib import admin
from rorapp.models import Faction

@admin.register(Faction)
class Faction(admin.ModelAdmin):
    list_display = ('game', 'position', 'player')
