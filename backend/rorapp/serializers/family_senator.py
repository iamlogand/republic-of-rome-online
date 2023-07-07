from rest_framework import serializers
from rorapp.models import FamilySenator


class FamilySenatorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FamilySenator
        fields = ('id', 'name', 'game', 'faction')
