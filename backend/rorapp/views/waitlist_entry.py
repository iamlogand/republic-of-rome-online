from rest_framework import viewsets
from rest_framework import status
from rorapp.models import WaitlistEntry
from rorapp.serializers import WaitlistEntryCreateSerializer
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

class WaitlistEntryViewSet(viewsets.ModelViewSet):
    queryset = WaitlistEntry.objects.all()
    serializer_class = WaitlistEntryCreateSerializer
    
    def create(self, request):
        data = request.data
        entry, created = WaitlistEntry.objects.get_or_create(**data)

        serializer = self.serializer_class(entry)

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

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