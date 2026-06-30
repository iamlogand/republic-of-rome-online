from django.db import models

from rorapp.models.game import Game


class Province(models.Model):
    game = models.ForeignKey(
        Game, related_name="provinces", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=20)
    developed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "name"], name="unique_province_game_name"
            )
        ]
