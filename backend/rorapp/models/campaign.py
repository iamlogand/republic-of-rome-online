from django.db import models
from django.utils.timezone import now

from rorapp.models.game import Game
from rorapp.models.senator import Senator
from rorapp.models.war import War


class Campaign(models.Model):
    game = models.ForeignKey(Game, related_name="campaigns", on_delete=models.CASCADE)
    commander = models.ForeignKey(
        Senator,
        related_name="campaigns",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    master_of_horse = models.ForeignKey(
        Senator,
        related_name="supporting_campaigns",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    war = models.ForeignKey(War, related_name="campaigns", on_delete=models.CASCADE)
    pending = models.BooleanField(default=False)
    imminent = models.BooleanField(default=False)
