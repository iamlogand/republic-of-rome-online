from django.db import models
from rorapp.models.game import Game
from rorapp.models.faction import Faction


# Model for representing senators
class Senator(models.Model):
    name = models.CharField(max_length=10)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, null=True, on_delete=models.SET_NULL)
    
    # String representation of the senator, used in admin site
    def __str__(self):
        return f'{self.name} in {self.game}'
