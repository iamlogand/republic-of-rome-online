from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from rorapp.models.game import Game


class GameParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    join_date = models.DateTimeField(default=timezone.now)
