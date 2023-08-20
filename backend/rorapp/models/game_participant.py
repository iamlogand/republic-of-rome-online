from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from rorapp.models.game import Game


# Model for representing game participants
class GameParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    join_date = models.DateTimeField(default=timezone.now)
    
    # String representation of the game participant, used in admin site
    def __str__(self):
        return f'{self.user} in {self.game}'
