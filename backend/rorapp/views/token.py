from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rorapp.serializers import TokenObtainPairByEmailViewSerializer
from django.core.exceptions import ObjectDoesNotExist

class TokenObtainPairByEmailView(CreateAPIView):
    """
    Takes an email and password pair as user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    
    serializer_class = TokenObtainPairByEmailViewSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            username = User.objects.get(email=request.data["email"]).username
            user = authenticate(username=username, password=request.data["password"])
        except ObjectDoesNotExist:
            user = None
        
        if user is not None: 
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': username
            })
        else:
            return Response({
                'detail': 'No active account found with the given credentials'
            })
