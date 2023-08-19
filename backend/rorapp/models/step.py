from django.db import models
from rorapp.models.phase import Phase


# Model for representing steps
class Step(models.Model):
    index = models.PositiveIntegerField()
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)

    # String representation of the step, used in admin site
    def __str__(self):
        return f'Step {self.index} in {self.phase.turn.game}'
