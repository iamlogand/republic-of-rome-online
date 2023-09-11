from django.contrib import admin
from rorapp.models import Senator


# Admin configuration for senators
@admin.register(Senator)
class SenatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'game', 'faction', 'alive')
