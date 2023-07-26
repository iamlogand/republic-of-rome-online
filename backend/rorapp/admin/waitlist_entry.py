from django.contrib import admin
from rorapp.models import WaitlistEntry


# Admin configuration for waitlist entries
@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
	list_display = ('id', "email", "entry_date")
