from django.db import models
from rorapp.models.senator import Senator
from rorapp.models.notification import Notification


# Model for representing relationships between senators and notifications

class SenatorNotification(models.Model):
    senator = models.ForeignKey(Senator, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
