from django.contrib import admin
from rorapp.models import SenatorActionLog


# Admin configuration for action_logs
@admin.register(SenatorActionLog)
class SenatorActionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'senator', 'action_log')
