from rest_framework import serializers
from rorapp.models import Game


class GameSerializer(serializers.ModelSerializer):
    host = serializers.ReadOnlyField(source='host.username')
    participants = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = ('id', 'name', 'description', 'creation_date', 'start_date', 'host', 'participants', 'step')
        read_only_fields = ['id', 'name', 'description', 'creation_date', 'start_date', 'host', 'participants', 'step']
        
    def get_participants(self, obj):
        participant_data = [{
            'id': participant.id,
            'username': participant.user.username,
            'join_date': participant.join_date
        } for participant in obj.gameparticipant_set.all()]
        
        return participant_data
        
        
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
