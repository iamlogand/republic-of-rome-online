from rest_framework import serializers
from rorapp.models import Title


# Serializer used to read titles
class TitleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Title
        fields = ('id', 'name', 'senator', 'start_step', 'end_step')
