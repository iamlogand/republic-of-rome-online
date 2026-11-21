from rest_framework import serializers

from rorapp.models.pending_decision import PendingDecision


class PendingDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingDecision
        fields = ["faction", "description"]
