from rest_framework import serializers
from rorapp.models import Game


class GameReadSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = Game
        fields = ('id', 'name', 'description', 'creation_date', 'start_date', 'owner')
        
        
class GameCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Game
        fields = ('name', 'description', 'owner')
        
        
class GameUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Game
        fields = ('name', 'description', 'creation_date', 'start_date', 'owner')
        read_only_fields = ['name', 'creation_date', 'start_date', 'owner']
