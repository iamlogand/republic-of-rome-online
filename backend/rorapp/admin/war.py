from django.contrib import admin

from rorapp.models import War


@admin.register(War)
class WarAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "name", "series_name", "index", "status")
