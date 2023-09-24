from django.contrib import admin
from rorapp.models import SenatorNotification


# Admin configuration for notifications
@admin.register(SenatorNotification)
class SenatorNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'senator', 'notification')
