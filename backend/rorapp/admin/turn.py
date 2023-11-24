from django.contrib import admin
from rorapp.models import Turn


# Admin configuration for turns
@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ("__str__", 'index', 'game')
