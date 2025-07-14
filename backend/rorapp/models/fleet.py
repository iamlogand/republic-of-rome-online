import roman
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from rorapp.models.game import Game


class Fleet(models.Model):
    game = models.ForeignKey(Game, related_name="fleets", on_delete=models.CASCADE)
    number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(25)]
    )

    @property
    def name(self):
        return roman.toRoman(self.number)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "number"], name="unique_fleet_game_number"
            )
        ]
