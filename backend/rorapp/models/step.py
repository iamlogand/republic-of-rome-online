from django.db import models
from rorapp.models.phase import Phase


# Model for representing steps
class Step(models.Model):
    index = models.PositiveIntegerField()
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)
