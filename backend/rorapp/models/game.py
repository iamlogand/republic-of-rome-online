from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Game(models.Model):
    name = models.CharField(max_length=100, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=now)
    started_on = models.DateTimeField(blank=True, null=True)
