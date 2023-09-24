from django.db import models
from rorapp.models.senator import Senator
from rorapp.models.action_log import ActionLog


# Model for representing relationships between senators and action_logs

class SenatorActionLog(models.Model):
    senator = models.ForeignKey(Senator, on_delete=models.CASCADE)
    action_log = models.ForeignKey(ActionLog, on_delete=models.CASCADE)
