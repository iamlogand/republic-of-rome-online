from django.contrib import admin
from rorapp.models import Notification


# Admin configuration for notifications
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'index', 'step', 'type', 'faction')
