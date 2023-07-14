from django.contrib import admin
from rorapp.models import Faction, FamilySenator


# Inline list showing related Senators
class FamilySenatorInline(admin.TabularInline):
    model = FamilySenator
    extra = 0
    

# Admin configuration for Faction
@admin.register(Faction)
class Faction(admin.ModelAdmin):
    list_display = ('id', 'game', 'position', 'player')
    inlines = [FamilySenatorInline]
