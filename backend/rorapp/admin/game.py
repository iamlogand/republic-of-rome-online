from django.contrib import admin
from rorapp.models import Game
from django.urls import path

from rorapp.views.execute_effects import execute_effects_view


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "execute-effects/<int:game_id>/",
                self.admin_site.admin_view(self.execute_effects),
                name="execute_effects",
            ),
        ]
        return custom_urls + urls

    def execute_effects(self, request, game_id):
        response = execute_effects_view(request, game_id)
        return response
