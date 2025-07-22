from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rorapp.models.game import Game
from rorapp.models.senator import Senator
from rorapp.models.war import War


class CombatCalculation(models.Model):
    game = models.ForeignKey(
        Game, related_name="combat_calculations", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    commander = models.ForeignKey(
        Senator,
        related_name="combat_calculations",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    war = models.ForeignKey(
        War,
        related_name="combat_calculations",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    land_battle = models.BooleanField(default=True)
    legions = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(25)]
    )
    veteran_legions = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(25)]
    )
    fleets = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(25)]
    )
