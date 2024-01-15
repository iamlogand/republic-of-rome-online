from django.db import models
from rorapp.models.faction import Faction


# Model for representing faction secrets (i.e. faction cards held by players)
class Secret(models.Model):
    name = models.CharField(max_length=17)
    TYPE_CHOICES = [
        ("M", "statesman"),
        ("I", "intrigue"),
        ("C", "concession"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    faction = models.ForeignKey(
        Faction, blank=True, null=True, on_delete=models.SET_NULL
    )
