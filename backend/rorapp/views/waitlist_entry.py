from rest_framework import viewsets
from rest_framework import status
from rorapp.models import WaitlistEntry
from rorapp.serializers import WaitlistEntryCreateSerializer
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

class CustomRateThrottle(UserRateThrottle):
    rate = "10/hour"

class WaitlistEntryViewSet(viewsets.ModelViewSet):
    queryset = WaitlistEntry.objects.all()
    serializer_class = WaitlistEntryCreateSerializer
    throttle_classes = [CustomRateThrottle]
    
    def create(self, request, *args, **kwargs):
        data = request.data

        isEntryPresent = WaitlistEntry.objects.filter(email=data["email"])

        if isEntryPresent:
            return Response({}, status=status.HTTP_200_OK)
        else:
            return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')
    
    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')
    
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')
    
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')
    
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')