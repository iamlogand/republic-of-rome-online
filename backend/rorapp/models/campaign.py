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
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    pending = models.BooleanField(default=False)
    imminent = models.BooleanField(default=False)

    # Turn states
    recently_deployed = models.BooleanField(default=True)
    recently_reinforced = models.BooleanField(default=False)

    @property
    def land_victory(self) -> bool:
        return self.war.status == War.Status.DEFEATED

    @property
    def rebel_army(self) -> bool:
        """The army of a Senator in revolt, which the Senate cannot command (1.11.3)."""

        return bool(self.commander and self.commander.rebel)

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
