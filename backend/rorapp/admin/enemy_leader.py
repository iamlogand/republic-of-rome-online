from django.contrib import admin

from rorapp.models import EnemyLeader


@admin.register(EnemyLeader)
class EnemyLeaderAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "game",
        "name",
        "series_name",
        "strength",
        "disaster_number",
        "standoff_number",
    )
