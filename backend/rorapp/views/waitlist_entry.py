from rest_framework import viewsets
from rorapp.models import WaitlistEntry
from rorapp.serializers import WaitlistEntryCreateSerializer

class WaitlistEntryViewSet(viewsets.ModelViewSet):
	queryset = WaitlistEntry.objects.all()
	serializer_class = WaitlistEntryCreateSerializer