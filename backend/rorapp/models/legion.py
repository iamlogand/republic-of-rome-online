import roman
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from rorapp.models.campaign import Campaign
from rorapp.models.game import Game
from rorapp.models.senator import Senator


class Legion(models.Model):
    game = models.ForeignKey(Game, related_name="legions", on_delete=models.CASCADE)
    number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(25)]
    )
    veteran = models.BooleanField(default=False)
    allegiance = models.ForeignKey(
        Senator,
        related_name="legions_in_allegiance",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    campaign = models.ForeignKey(
        Campaign,
        related_name="legions",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    @property
    def name(self):
        return roman.toRoman(self.number)

    @property
    def strength(self):
        return 2 if self.veteran else 1

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "number"], name="unique_legion_game_number"
            )
        ]
