from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from rorapp.models.game import Game
from rorapp.models.senator import Senator


class Province(models.Model):
    game = models.ForeignKey(
        Game, related_name="provinces", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=20)
    developed = models.BooleanField(default=False)
    frontier = models.BooleanField(default=False)
    governor = models.ForeignKey(
        Senator,
        related_name="governed_provinces",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    term = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
    )
    elected_this_turn = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "name"], name="unique_province_game_name"
            )
        ]
