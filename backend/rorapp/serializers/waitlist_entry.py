from rest_framework import serializers
from rorapp.models import WaitlistEntry

class WaitlistEntryCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = WaitlistEntry
		fields = ('email', 'entry_date')