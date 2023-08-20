from django.contrib import admin
from rorapp.models import FamilySenator


# Admin configuration for family senators
@admin.register(FamilySenator)
class FamilySenatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'game', 'faction')
