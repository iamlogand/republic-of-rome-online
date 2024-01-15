from django.db import models
from rorapp.models.faction import Faction


# Model for representing faction secrets (i.e. faction cards held by players)
class Secret(models.Model):
    name = models.CharField(max_length=40)
    TYPE_CHOICES = [
        ("statesman", "statesman"),
        ("intrigue", "intrigue"),
        ("concession", "concession"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
