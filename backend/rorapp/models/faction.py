from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from rorapp.models.game import Game


class Faction(models.Model):
    game = models.ForeignKey(Game, related_name='factions', on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "position"], name="unique_game_position"
            ),
            models.UniqueConstraint(
                fields=["game", "player"], name="unique_game_player"
            ),
        ]
