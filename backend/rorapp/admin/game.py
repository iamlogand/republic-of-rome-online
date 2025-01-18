from django.contrib import admin

from rorapp.models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name")
