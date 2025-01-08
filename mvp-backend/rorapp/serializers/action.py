from rest_framework import serializers
from rorapp.models import Action


# Serializer used to read actions
class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = (
            "id",
            "step",
            "faction",
            "type",
            "required",
            "parameters",
            "completed",
        )
