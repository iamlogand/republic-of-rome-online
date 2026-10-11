from django.db import models

from rorapp.models.faction import Faction
from rorapp.models.game import Game


class PendingDecision(models.Model):
    game = models.ForeignKey(
        Game, related_name="pending_decisions", on_delete=models.CASCADE
    )
    faction = models.ForeignKey(
        Faction, related_name="pending_decisions", on_delete=models.CASCADE
    )
    description = models.CharField(max_length=200)
