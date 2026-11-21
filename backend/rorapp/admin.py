from django.contrib import admin

from rorapp.models.pending_decision import PendingDecision


@admin.register(PendingDecision)
class PendingDecisionAdmin(admin.ModelAdmin):
    list_display = ["id", "game", "faction", "description"]
    list_filter = ["game"]
