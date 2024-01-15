from django.contrib import admin
from rorapp.models import Situation

# Admin configuration for situations
@admin.register(Situation)
class SituationAdmin(admin.ModelAdmin):
    list_display = ("__str__", 'name', 'type', 'secret', 'game', 'index')