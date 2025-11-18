from django.db import models

from rorapp.models.game import Game
from rorapp.models.senator import Senator
from rorapp.models.war import War


class Campaign(models.Model):
    game = models.ForeignKey(Game, related_name="campaigns", on_delete=models.CASCADE)
    war = models.ForeignKey(War, related_name="campaigns", on_delete=models.CASCADE)
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
    pending = models.BooleanField(default=False)
    imminent = models.BooleanField(default=False)

    # Turn states
    recently_deployed_or_reinforced = models.BooleanField(default=True)

    @property
    def display_name(self) -> str:
        if self.commander:
            commander_name = self.commander.display_name
            return (
                commander_name
                + ("'" if commander_name.endswith("s") else "'s")
                + " campaign"
            )
        else:
            return "uncommanded campaign"
