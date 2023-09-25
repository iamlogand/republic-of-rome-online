from django.db import models
from rorapp.models.turn import Turn


# Model for representing phases
class Phase(models.Model):
    name = models.CharField(max_length=10)
    index = models.PositiveIntegerField()
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE)
    
    # String representation of the phase, used in admin site
    def __str__(self):
        return f'{self.id}: {self.name} phase of turn {self.turn.index} in {self.turn.game}'
