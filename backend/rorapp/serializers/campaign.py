from rest_framework import serializers

from rorapp.models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "id",
            "game",
            "commander",
            "master_of_horse",
            "war",
            "display_name",
        ]
