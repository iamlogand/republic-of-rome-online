from django.db import models
from rorapp.models.game import Game
from rorapp.models.faction import Faction
from rorapp.models.step import Step


# Model for representing senators
class Senator(models.Model):
    name = models.CharField(max_length=10)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="senators")
    faction = models.ForeignKey(
        Faction, blank=True, null=True, on_delete=models.SET_NULL
    )
    death_step = models.ForeignKey(
        Step, on_delete=models.CASCADE, blank=True, null=True
    )  # Null means the senator is alive
    code = models.IntegerField()
    generation = models.IntegerField(default=1)
    rank = models.IntegerField(blank=True, null=True)

    # Fixed attributes
    military = models.IntegerField()
    oratory = models.IntegerField()
    loyalty = models.IntegerField()

    # Variable attributes
    influence = models.IntegerField()
    popularity = models.IntegerField(default=0)
    knights = models.IntegerField(default=0)
    talents = models.IntegerField(default=0)

    @property
    def votes(self):
        return self.oratory + self.knights
