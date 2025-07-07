import roman
from enum import Enum
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from rorapp.models.faction import Faction
from rorapp.models.game import Game


class Senator(models.Model):

    class StatusItem(Enum):
        ABSTAINED = "Abstained"
        CONTRIBUTED = "Contributed"
        VOTED_NAY = "Voted nay"
        VOTED_YEA = "Voted yea"
        INCOMING_CONSUL = "Incoming consul"
        PREFERS_FIELD_CONSUL = "Prefers Field Consul"
        PREFERS_ROME_CONSUL = "Prefers Rome Consul"

    class Title(Enum):
        FACTION_LEADER = "Faction leader"
        FIELD_CONSUL = "Field Consul"
        HRAO = "HRAO"
        ROME_CONSUL = "Rome Consul"
        PRESIDING_MAGISTRATE = "Presiding magistrate"

    game = models.ForeignKey(Game, related_name="senators", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=3)
    faction = models.ForeignKey(
        Faction,
        related_name="senators",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    alive = models.BooleanField(default=True)
    military = models.IntegerField(validators=[MinValueValidator(0)])
    oratory = models.IntegerField(validators=[MinValueValidator(0)])
    loyalty = models.IntegerField(validators=[MinValueValidator(0)])
    influence = models.IntegerField(validators=[MinValueValidator(0)])
    popularity = models.IntegerField(
        default=0, validators=[MinValueValidator(-9), MaxValueValidator(9)]
    )
    knights = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    talents = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    generation = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    status_items = models.JSONField(default=list, blank=True)
    titles = models.JSONField(default=list, blank=True)

    @property
    def votes(self):
        return self.oratory + self.knights

    @property
    def display_name(self) -> str:
        return (
            self.name
            if self.generation == 1
            else f"{self.name} {roman.toRoman(self.generation)}"
        )

    def add_status_item(self, status: StatusItem) -> None:
        if status.value not in self.status_items:
            self.status_items.append(status.value)
            self.save()

    def remove_status_item(self, status: StatusItem) -> None:
        if status.value in self.status_items:
            self.status_items.remove(status.value)
            self.save()

    def has_status_item(self, status: StatusItem) -> bool:
        return status.value in self.status_items

    def add_title(self, title: Title) -> None:
        if title.value not in self.titles:
            self.titles.append(title.value)
            self.save()

    def remove_title(self, title: Title) -> None:
        if title.value in self.titles:
            self.titles.remove(title.value)
            self.save()

    def has_title(self, title: Title) -> bool:
        return title.value in self.titles
