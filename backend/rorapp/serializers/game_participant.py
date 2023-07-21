from rest_framework import serializers
from rorapp.models import GameParticipant


# Serializer used to read and delete game participants
class GameParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameParticipant
        fields = ('id', 'user', 'game', 'join_date')


# Serializer used to create game participants
class GameParticipantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameParticipant
        fields = ('game',)
