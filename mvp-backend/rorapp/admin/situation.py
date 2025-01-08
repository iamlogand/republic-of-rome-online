from django.contrib import admin
from rorapp.models import Situation


# Admin configuration for situations
@admin.register(Situation)
class SituationAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "type", "secret", "name", "index")
    list_filter = ("type", "secret")
    search_fields = (
        "id",
        "game__id",
        "name",
        "index",
    )
