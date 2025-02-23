from django.contrib import admin

from rorapp.models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "created_on", "text")
