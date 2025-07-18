from django.db import models
from django.core.validators import MinValueValidator

from rorapp.models.game import Game


class War(models.Model):

    class Status(models.TextChoices):
        INACTIVE = "Inactive", "Inactive"
        IMMINENT = "Imminent", "Imminent"
        ACTIVE = "Active", "Active"

    game = models.ForeignKey(Game, related_name="wars", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    series_name = models.CharField(max_length=20, blank=True, null=True)
    index = models.IntegerField(validators=[MinValueValidator(0)])
    land_strength = models.IntegerField(validators=[MinValueValidator(1)])
    fleet_support = models.IntegerField(validators=[MinValueValidator(0)])
    naval_strength = models.IntegerField(validators=[MinValueValidator(0)])
    disaster_numbers = models.JSONField(default=list, blank=True)
    standoff_numbers = models.JSONField(default=list, blank=True)
    spoils = models.IntegerField(validators=[MinValueValidator(0)])
    famine = models.BooleanField(default=False)
    location = models.CharField(max_length=20)

    status = models.CharField(max_length=12, choices=Status.choices)
    undefeated_navy = models.BooleanField(default=False)
    unprosecuted = models.BooleanField(default=False)
