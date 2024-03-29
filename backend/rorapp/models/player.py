from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from rorapp.models.game import Game


# Model for representing game players
class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
    join_date = models.DateTimeField(default=timezone.now)
