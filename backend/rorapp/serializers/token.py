from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView


class TokenObtainPairByEmailViewSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
