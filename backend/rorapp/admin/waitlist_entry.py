from django.contrib import admin
from rorapp.models import WaitlistEntry

@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
	list_display = ("email", "entry_date")