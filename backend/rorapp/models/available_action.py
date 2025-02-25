from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from rorapp.models.faction import Faction
from rorapp.models.game import Game


class AvailableAction(models.Model):
    game = models.ForeignKey(Game, related_name="actions", on_delete=models.CASCADE)
    faction = models.ForeignKey(
        Faction, related_name="factions", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    position = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    schema = models.JSONField(default=list, blank=True)
