from django.contrib import admin
from rorapp.models import WaitlistEntry


# Admin configuration for waitlist entries
@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
	list_display = ("__str__", "email", "entry_date")
