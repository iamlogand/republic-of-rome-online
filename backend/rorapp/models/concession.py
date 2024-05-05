from django.db import models
from rorapp.models.game import Game
from rorapp.models.senator import Senator


# Model for representing concessions
class Concession(models.Model):
    name = models.CharField(max_length=13)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    senator = models.ForeignKey(
        Senator, blank=True, null=True, on_delete=models.CASCADE
    )
