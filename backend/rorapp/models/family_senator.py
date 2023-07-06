from django.db import models
from rorapp.models.game import Game
from rorapp.models.faction import Faction


class FamilySenator(models.Model):
    name = models.CharField(max_length=10)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f'{self.name} in {self.game}'
