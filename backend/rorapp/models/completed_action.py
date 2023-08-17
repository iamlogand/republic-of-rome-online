from django.db import models
from rorapp.models.step import Step


# Model for representing actions that a player has taken
class CompletedAction(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    type = models.PositiveIntegerField()
    parameters = models.JSONField()
