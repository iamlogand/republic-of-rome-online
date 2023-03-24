from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.name
