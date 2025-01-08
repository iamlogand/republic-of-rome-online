from django.db import models
from django.utils import timezone


class WaitlistEntry(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    entry_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "waitlist entries"
