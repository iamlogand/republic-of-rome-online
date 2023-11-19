from django.db import models
from rorapp.models.step import Step
from rorapp.models.faction import Faction


# Model for representing actions that a player could take or has taken
class Action(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    required = models.BooleanField()
    parameters = models.JSONField(blank=True, null=True)
    completed = models.BooleanField(
        default=False
    )  # Incomplete actions are known as "potential actions" because they may never be completed
