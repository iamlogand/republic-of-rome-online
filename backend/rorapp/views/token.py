from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rorapp.serializers import MyTokenObtainPairSerializer, TokenObtainPairByEmailSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class TokenObtainPairByEmailView(CreateAPIView):
    """
    Takes an email and password pair as user credentials and returns an access and refresh JSON web token pair to prove the authentication of those credentials.
    Used when signing in by email instead of by username. 
    """

    serializer_class = TokenObtainPairByEmailSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Attempt to authenticate the request
        try:
            user = User.objects.get(email=request.data["email"])
            user = authenticate(
                username=user.username,
                password=request.data["password"]
            )
        except ObjectDoesNotExist:
            user = None

        if user is not None:
            # If authentication succeeds then generate a new refresh token and access token
            # to send in the response
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'id': user.id
                },
                status=status.HTTP_200_OK
            )
        else:
            # If authentication fails then respond with a 401 status
            return Response(
                {
                    'detail': 'No active account found with the given credentials'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
