from django.contrib import admin
from rorapp.models import Fleet


@admin.register(Fleet)
class FleetAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "number")
