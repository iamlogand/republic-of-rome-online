from django.contrib import admin
from rorapp.models import Senator


# Admin configuration for senators
@admin.register(Senator)
class SenatorAdmin(admin.ModelAdmin):
    list_display = ("__str__", 'name', 'game', 'faction', 'death_step', 'code', 'generation', 'rank')
