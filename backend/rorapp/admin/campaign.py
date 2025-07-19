from django.contrib import admin
from rorapp.models import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "commander", "master_of_horse", "war")
