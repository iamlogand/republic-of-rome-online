from django.contrib import admin
from rorapp.models import Secret


# Admin configuration for secrets
@admin.register(Secret)
class SecretAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "faction", "type", "name")
    list_filter = ("type",)
    search_fields = (
        "id",
        "faction__game__id",
        "name",
    )

    @admin.display(ordering="faction__game__id")
    def game(self, obj):
        return obj.faction.game
