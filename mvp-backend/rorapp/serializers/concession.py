from rest_framework import serializers
from rorapp.models import Concession


# Serializer used to read concessions
class ConcessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concession
        fields = ("id", "name", "game", "senator")
