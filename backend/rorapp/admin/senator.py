from django.contrib import admin
from rorapp.models import Senator


# Admin configuration for senators
@admin.register(Senator)
class SenatorAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "game",
        "faction",
        "name",
        "code",
        "generation",
        "death_step",
        "rank",
    )
    search_fields = (
        "game__id",
        "faction__id",
        "name",
        "code",
        "generation",
        "death_step__id",
        "rank",
    )
