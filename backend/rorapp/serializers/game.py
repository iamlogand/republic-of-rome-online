from rest_framework import serializers
from rorapp.models import Game


class GameReadSerializer(serializers.ModelSerializer):
    host = serializers.ReadOnlyField(source='host.username')
    participants = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = ('id', 'name', 'description', 'creation_date', 'start_date', 'host', 'participants')
        
    def get_participants(self, obj):
        return [{'id': participant.id, 'username': participant.user.username} for participant in obj.gameparticipant_set.all()]
        
        
class GameCreateSerializer(serializers.ModelSerializer):
    host = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Game
        fields = ('id', 'name', 'description', 'owner')
        
        
class GameUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Game
        fields = ('name', 'description', 'creation_date', 'start_date', 'host')
        read_only_fields = ['name', 'creation_date', 'start_date', 'host']
