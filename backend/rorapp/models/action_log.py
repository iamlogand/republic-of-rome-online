from django.db import models
from rorapp.models.step import Step
from rorapp.models.faction import Faction


# Model for representing action_logs
class ActionLog(models.Model):
    index = models.PositiveIntegerField()
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    faction = models.ForeignKey(
        Faction, on_delete=models.CASCADE, blank=True, null=True
    )
    data = models.JSONField(blank=True, null=True)
