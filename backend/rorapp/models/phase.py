from django.db import models
from rorapp.models.turn import Turn


# Model for representing phases
class Phase(models.Model):
    name = models.CharField(max_length=10)
    index = models.PositiveIntegerField()
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE)
