from django.utils.timezone import now
from django.db import models

from rorapp.models.game import Game


class Log(models.Model):

    game = models.ForeignKey(Game, related_name="logs", on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=now)
    text = models.TextField()
