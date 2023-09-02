from rest_framework import serializers
from rorapp.models import Notification


# Serializer used to read notifications
class NotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notification
        fields = ('id', 'index', 'step', 'type', 'faction', 'data')
