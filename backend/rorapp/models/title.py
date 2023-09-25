from django.db import models
from rorapp.models.senator import Senator
from rorapp.models.step import Step


# Model for representing titles
class Title(models.Model):
    name = models.CharField(max_length=21)
    senator = models.ForeignKey(Senator, on_delete=models.CASCADE)
    start_step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='starting_title_set')
    end_step = models.ForeignKey(Step, on_delete=models.CASCADE, blank=True, null=True, related_name='ending_title_set')  # Null means the title is active
    major_office = models.BooleanField(default=False)
    
    # String representation of the title, used in admin site
    def __str__(self):
        return f'{self.id}: {self.name} {self.senator}'
