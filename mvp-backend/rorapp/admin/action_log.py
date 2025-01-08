from django.contrib import admin
from rorapp.models import ActionLog


# Admin configuration for action_logs
@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ("__str__", "index", "step", "type", "faction")
