from django.contrib import admin
from rorapp.models import Faction, FamilySenator


class FamilySenatorInline(admin.TabularInline):
    model = FamilySenator
    extra = 0
    

@admin.register(Faction)
class Faction(admin.ModelAdmin):
    list_display = ('game', 'position', 'player')
    inlines = [FamilySenatorInline]
