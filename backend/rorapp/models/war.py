from django.db import models
from rorapp.models.game import Game


# Model for representing wars
class War(models.Model):
    name = models.CharField(max_length=10)
    index = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    land_strength = models.IntegerField()
    fleet_support = models.IntegerField()
    naval_strength = models.IntegerField()
    disaster_numbers = models.JSONField()
    standoff_numbers = models.JSONField()
    spoils = models.IntegerField()
    STATUS_CHOICES = [
        ("inactive", "inactive"),
        ("imminent", "imminent"),
        ("active", "active"),
        ("unprosecuted", "unprosecuted"),
        ("defeated", "defeated"),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    undefeated_navy = models.BooleanField()
    famine = models.BooleanField()
