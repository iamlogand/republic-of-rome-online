from django.contrib import admin
from rorapp.models import FamilySenator

@admin.register(FamilySenator)
class FamilySenator(admin.ModelAdmin):
    list_display = ('name', 'game', 'faction')
