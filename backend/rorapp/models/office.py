from django.utils import timezone
from django.db import models
from rorapp.models import FamilySenator


# Model for representing offices
class Office(models.Model):
    name = models.CharField(max_length=21)
    senator = models.ForeignKey(FamilySenator, on_delete=models.CASCADE)
    start_step = models.IntegerField()
    end_step = models.IntegerField(blank=True, null=True)
    
    # String representation of the office, used in admin site
    def __str__(self):
        return f'{self.name} {self.senator}'
