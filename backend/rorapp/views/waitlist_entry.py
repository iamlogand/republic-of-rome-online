from rest_framework import viewsets
from rorapp.models import WaitlistEntry
from rorapp.serializers import WaitlistEntryCreateSerializer
from rest_framework.exceptions import MethodNotAllowed

class WaitlistEntryViewSet(viewsets.ModelViewSet):
    queryset = WaitlistEntry.objects.all()
    serializer_class = WaitlistEntryCreateSerializer
    
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