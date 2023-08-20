from rest_framework import serializers
from rorapp.models import PotentialAction


# Serializer used to read potential actions
class PotentialActionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PotentialAction
        fields = ('id', 'step', 'faction', 'type', 'required')
