from rest_framework import serializers
from rorapp.models import GameParticipant
from rorapp.serializers.user import UserSerializer


# Serializer used to read and delete game participants
class GameParticipantSerializer(serializers.ModelSerializer):    
    class Meta:
        model = GameParticipant
        fields = ('id', 'user', 'game', 'join_date')
        

# Serializer used to read game participants in detail and prefetch users
class GameParticipantDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GameParticipant
        fields = ('id', 'user', 'game', 'join_date')


# Serializer used to create game participants
class GameParticipantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameParticipant
        fields = ('game',)
