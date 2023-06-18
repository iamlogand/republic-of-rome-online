from django.db import models
from django.utils import timezone

class WaitlistEntry(models.Model):
	email = models.EmailField(max_length=254, unique=TRUE)
	entry_date = models.DateTimeField(default=timezone.now)