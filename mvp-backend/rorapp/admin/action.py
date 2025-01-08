from django.contrib import admin
from rorapp.models import Action


# Admin configuration for actions
@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "game",
        "step",
        "faction",
        "type",
        "required",
        "completed",
    )
    list_filter = ("required", "completed")
    search_fields = (
        "id",
        "step__phase__turn__game__id",
        "step__id",
        "faction__id",
        "type",
    )

    @admin.display(ordering="step__phase__turn__game__id")
    def game(self, obj):
        return obj.step.phase.turn.game
