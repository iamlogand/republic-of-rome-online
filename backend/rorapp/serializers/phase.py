from rest_framework import serializers
from rorapp.models import Phase


# Serializer used to read phases
class PhaseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Phase
        fields = ('id', 'name', 'index', 'turn')
