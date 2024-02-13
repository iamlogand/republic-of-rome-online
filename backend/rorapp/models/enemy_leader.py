from django.db import models
from rorapp.models.game import Game
from rorapp.models.war import War


# Model for representing enemy leaders
class EnemyLeader(models.Model):
    name = models.CharField(max_length=13)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    strength = models.IntegerField()
    disaster_number = models.IntegerField()
    standoff_number = models.IntegerField()
    war_name = models.CharField(max_length=10)
    current_war = models.ForeignKey(War, on_delete=models.CASCADE)
    dead = models.BooleanField()
