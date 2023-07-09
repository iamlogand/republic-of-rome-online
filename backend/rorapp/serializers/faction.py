from rest_framework import serializers
from rorapp.models import Faction


class FactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Faction
        fields = ('id', 'game', 'position', 'player')
