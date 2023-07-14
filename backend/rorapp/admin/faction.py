from django.contrib import admin
from rorapp.models import Faction, FamilySenator


# Inline table showing related senators
class FamilySenatorInline(admin.TabularInline):
    model = FamilySenator
    extra = 0
    

# Admin configuration for factions
@admin.register(Faction)
class Faction(admin.ModelAdmin):
    list_display = ('id', 'game', 'position', 'player')
    inlines = [FamilySenatorInline]
