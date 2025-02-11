from django.db import models

from rorapp.models.faction import Faction
from rorapp.models.game import Game


class AvailableAction(models.Model):
    game = models.ForeignKey(Game, related_name="actions", on_delete=models.CASCADE)
    faction = models.ForeignKey(
        Faction, related_name="factions", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    schema = models.JSONField(default=list)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "faction", "name"], name="unique_game_faction_name"
            ),
        ]
