from django.contrib import admin
from rorapp.models import ActionLog


# Admin configuration for action_logs
@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'index', 'step', 'type', 'faction')
