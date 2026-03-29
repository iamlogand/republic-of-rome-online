from django.db import models

from rorapp.models.game import Game


class EnemyLeader(models.Model):
    game = models.ForeignKey(
        Game, related_name="enemy_leaders", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=30)
    series_name = models.CharField(max_length=20)
    strength = models.IntegerField()
    disaster_number = models.IntegerField()
    standoff_number = models.IntegerField()
    active = models.BooleanField(default=False)
