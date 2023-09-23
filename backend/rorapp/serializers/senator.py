from rest_framework import serializers
from rorapp.models import Senator


# Serializer used to read senators
class SenatorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Senator
        fields = (
            'id',
            'name',
            'game',
            'faction',
            'alive',
            'code',
            'generation',
            'military',
            'oratory',
            'loyalty',
            'influence',
            'popularity',
            'knights',
            'talents',
            'votes'
        )
