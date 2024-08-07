from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Serializer used to obtain token pair via username
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user id to the response
        data["user_id"] = self.user.id
        return data


# Serializer used to obtain token pair via email
class TokenObtainPairByEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"})
