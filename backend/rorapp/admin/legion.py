from django.contrib import admin
from rorapp.models import Legion


@admin.register(Legion)
class LegionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "number", "veteran", "allegiance")
