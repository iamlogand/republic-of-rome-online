from django.db import models
from rorapp.models.senator import Senator


# Model for representing titles
class Title(models.Model):
    name = models.CharField(max_length=21)
    senator = models.ForeignKey(Senator, on_delete=models.CASCADE)
    start_step = models.IntegerField()
    end_step = models.IntegerField(blank=True, null=True)
    
    # String representation of the title, used in admin site
    def __str__(self):
        return f'{self.name} {self.senator}'
