from rest_framework import serializers
from rorapp.models import Step


# Serializer used to read steps
class StepSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Step
        fields = ('id', 'index', 'phase')
