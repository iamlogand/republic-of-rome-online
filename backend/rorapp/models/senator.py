from django.db import models
from rorapp.models.game import Game
from rorapp.models.faction import Faction


# Model for representing senators
class Senator(models.Model):
    name = models.CharField(max_length=10)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, blank=True, null=True, on_delete=models.SET_NULL)
    alive = models.BooleanField(default=True)
    code = models.IntegerField()
    generation = models.IntegerField(default=1)
    
    # Fixed attributes
    military = models.IntegerField()
    oratory = models.IntegerField()
    loyalty = models.IntegerField()
    
    # Variable attributes
    influence = models.IntegerField()
    popularity = models.IntegerField(default=0)
    knights = models.IntegerField(default=0)
    talents = models.IntegerField(default=0)
    
    @property
    def votes(self):
        return self.oratory + self.knights
    
    # String representation of the senator, used in admin site
    def __str__(self):
        return f'{self.name} in {self.game}'
