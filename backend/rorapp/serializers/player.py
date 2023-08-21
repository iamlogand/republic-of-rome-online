from rest_framework import serializers
from rorapp.models import Player
from rorapp.serializers.user import UserSerializer


# Serializer used to read and delete game players
class PlayerSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Player
        fields = ('id', 'user', 'game', 'join_date')
        

# Serializer used to read game players in detail and prefetch users
class PlayerDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Player
        fields = ('id', 'user', 'game', 'join_date')


# Serializer used to create game players
class PlayerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('game',)
