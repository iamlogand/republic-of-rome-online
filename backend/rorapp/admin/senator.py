from django.contrib import admin

from rorapp.models import Senator


@admin.register(Senator)
class SenatorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "name", "code", "faction", "alive")
