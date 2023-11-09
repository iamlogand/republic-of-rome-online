from django.db import models
from rorapp.models.game import Game
from rorapp.models.player import Player


# Model for representing factions
class Faction(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='factions')
    position = models.IntegerField() # 1 is red, 2 is yellow, 3 is green, 4 is cyan, 5 is blue, 6 is purple
    player = models.ForeignKey(Player, blank=True, null=True, on_delete=models.SET_NULL)
    rank = models.IntegerField(blank=True, null=True)
    
    # String representation of the faction, used in admin site
    def __str__(self):
        return f'{self.id}: faction {self.position} in {self.game}'
