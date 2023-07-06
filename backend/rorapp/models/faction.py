from django.db import models
from rorapp.models.game import Game
from rorapp.models.game_participant import GameParticipant


class Faction(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    position = models.IntegerField()
    player = models.ForeignKey(GameParticipant, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f'{self.game} faction {self.position}'
