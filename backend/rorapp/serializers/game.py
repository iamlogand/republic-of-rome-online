from rest_framework import serializers
from rorapp.models import Game
from rorapp.serializers.user import UserSerializer


class GameSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    
    class Meta:
        model = Game
        fields = ('name', 'description', 'owner', 'creation_date', 'start_date')
