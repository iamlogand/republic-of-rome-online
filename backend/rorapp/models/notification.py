from django.db import models
from rorapp.models.step import Step


# Model for representing notifications
class Notification(models.Model):
    index = models.PositiveIntegerField()
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    data = models.JSONField(blank=True, null=True)
