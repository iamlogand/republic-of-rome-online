from django.contrib import admin

from rorapp.models import AvailableAction


@admin.register(AvailableAction)
class AvailableActionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "faction", "type", "schema")
