from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from rorapp.models.faction import Faction
from rorapp.models.game import Game


class Senator(models.Model):
    game = models.ForeignKey(Game, related_name="senators", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=3)
    faction = models.ForeignKey(
        Faction,
        related_name="senators",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    alive = models.BooleanField(default=True)
    military = models.IntegerField(validators=[MinValueValidator(0)])
    oratory = models.IntegerField(validators=[MinValueValidator(0)])
    loyalty = models.IntegerField(validators=[MinValueValidator(0)])
    influence = models.IntegerField(validators=[MinValueValidator(0)])
    popularity = models.IntegerField(
        default=0, validators=[MinValueValidator(-9), MaxValueValidator(9)]
    )
    knights = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    talents = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    @property
    def votes(self):
        return self.oratory + self.knights
