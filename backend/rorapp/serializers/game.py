from rest_framework import serializers
from rorapp.models import Game
from rorapp.serializers.user import UserSerializer


class GameSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Game
        fields = ('name', 'description', 'creation_date', 'start_date', 'owner')
