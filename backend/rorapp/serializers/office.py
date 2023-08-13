from rest_framework import serializers
from rorapp.models import Office


# Serializer used to read offices
class OfficeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Office
        fields = ('id', 'name', 'senator', 'start_step', 'end_step')
