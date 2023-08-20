from django.db import models
from rorapp.models.game import Game
from rorapp.models.game_participant import GameParticipant


# Model for representing factions
class Faction(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    position = models.IntegerField()
    player = models.ForeignKey(GameParticipant, null=True, on_delete=models.SET_NULL)
    
    # String representation of the faction, used in admin site
    def __str__(self):
        return f'Faction {self.position} in {self.game}'
