from django.contrib import admin
from rorapp.models import SenatorActionLog


# Admin configuration for action_logs
@admin.register(SenatorActionLog)
class SenatorActionLogAdmin(admin.ModelAdmin):
    list_display = ("__str__", "senator", "action_log")
