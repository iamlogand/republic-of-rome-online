from django.contrib import admin
from rorapp.models import EnemyLeader


# Admin configuration for enemy leaders
@admin.register(EnemyLeader)
class EnemyLeaderAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "name",
        "game",
        "strength",
        "war_name",
        "current_war",
        "dead",
    )
