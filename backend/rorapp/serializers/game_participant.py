from rest_framework import serializers
from rorapp.models import GameParticipant


class GameParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameParticipant
        fields = ('user', 'game', 'join_date')
