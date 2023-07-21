from rest_framework import serializers
from django.contrib.auth.models import User


# Serializer used to read users
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)


# Serializer used to read users in detail
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
