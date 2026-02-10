from django.contrib import admin
from rorapp.models import Game
from django.urls import path

from rorapp.views.execute_effects import execute_effects_view
from rorapp.views.skip_to_next_phase import skip_to_next_phase_view


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name", "host", "created_on", "turn", "phase")

    readonly_fields = ("status", "votes_pending")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "execute-effects/<int:game_id>/",
                self.admin_site.admin_view(self.execute_effects),
                name="execute_effects",
            ),
            path(
                "skip-to-next-phase/<int:game_id>/",
                self.admin_site.admin_view(self.skip_to_next_phase),
                name="skip_to_next_phase",
            ),
        ]
        return custom_urls + urls

    def execute_effects(self, request, game_id):
        response = execute_effects_view(request, game_id)
        return response

    def skip_to_next_phase(self, request, game_id):
        response = skip_to_next_phase_view(request, game_id)
        return response
