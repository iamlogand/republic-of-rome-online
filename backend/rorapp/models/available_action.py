from django.core.validators import MinValueValidator
from django.db import models

from rorapp.models.faction import Faction
from rorapp.models.game import Game


class AvailableAction(models.Model):
    game = models.ForeignKey(Game, related_name="actions", on_delete=models.CASCADE)
    faction = models.ForeignKey(
        Faction, related_name="factions", on_delete=models.CASCADE
    )
    base_name = models.CharField(max_length=50)
    variant_name = models.CharField(max_length=50, null=True, blank=True)
    position = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    schema = models.JSONField(default=list, blank=True)
    context = models.JSONField(default=dict, blank=True)
    
    @property
    def name(self) -> str:
        """Returns the display name for this action (variant_name if set, otherwise base_name)"""
        return self.variant_name or self.base_name

    @property
    def identifier(self) -> str:
        return f"{self.game_id} {self.faction_id} {self.name}"
