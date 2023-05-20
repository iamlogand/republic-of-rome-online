from rest_framework import serializers
from rorapp.models import GameParticipant


class GameParticipantCreateSerializer(serializers.ModelSerializer):    
    class Meta:
        model = GameParticipant
        fields = ('game', 'join_date')
