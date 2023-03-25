from rest_framework import serializers


class TokenObtainPairByEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
