from rest_framework import serializers
from rorapp.models import Game


class GameSerializer(serializers.ModelSerializer):
    host = serializers.ReadOnlyField(source='host.username')
    
    class Meta:
        model = Game
        fields = ('id', 'name', 'description', 'creation_date', 'start_date', 'host', 'step')
        read_only_fields = ['id', 'name', 'description', 'creation_date', 'start_date', 'host', 'step']
        
        
class GameCreateSerializer(serializers.ModelSerializer):
    host = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Game
        fields = ('id', 'name', 'description', 'host')
        read_only_fields = ['id']
        
        
class GameUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Game
        fields = ('id', 'name', 'description', 'creation_date', 'start_date', 'host')
        read_only_fields = ['id', 'name', 'creation_date', 'start_date', 'host']
