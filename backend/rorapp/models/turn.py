from django.db import models
from rorapp.models.game import Game


# Model for representing turns
class Turn(models.Model):
    index = models.PositiveIntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    
    # String representation of the phase, used in admin site
    def __str__(self):
        return f'turn {self.index} of {self.game.index}'
