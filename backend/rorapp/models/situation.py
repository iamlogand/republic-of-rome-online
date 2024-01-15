from django.db import models
from rorapp.models.game import Game


# Model for representing situations (i.e. cards in the deck)
class Situation(models.Model):
    name = models.CharField(max_length=40)
    TYPE_CHOICES = [
        ("W", "war"),
        ("S", "senator"),
        ("M", "statesman"),
        ("L", "leader"),
        ("I", "intrigue"),
        ("C", "concession"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    secret = models.BooleanField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    index = models.IntegerField()
