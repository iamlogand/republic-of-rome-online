from typing import List, Optional

import roman
from enum import Enum
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from rorapp.classes.concession import Concession
from rorapp.models.faction import Faction
from rorapp.models.game import Game


class Senator(models.Model):

    class StatusItem(Enum):
        ABSTAINED = "abstained"
        ACCUSED = "accused"
        APPEALED_TO_PEOPLE = "appealed to people"
        CONTRIBUTED = "contributed"
        CONSENT_REQUIRED = "consent required"
        CORRUPT = "corrupt"
        MAJOR_CORRUPT = "major corrupt"
        PROSECUTOR = "prosecutor"
        SUGGESTED_DICTATOR = "suggested dictator"
        UNANIMOUSLY_DEFEATED = "unanimously defeated"
        STEPPED_DOWN = "stepped down"
        VOTED_NAY = "voted nay"
        VOTED_YEA = "voted yea"
        INCOMING_CONSUL = "incoming consul"
        PREFERS_FIELD_CONSUL = "prefers Field Consul"
        PREFERS_ROME_CONSUL = "prefers Rome Consul"
        PREFERRED_ATTACKER = "preferred attacker"
        CONSIDERING_LAND_BATTLE = "considering land battle"
        FREE_TRIBUNE = "free tribune"
        PERSUADER = "persuader"
        PERSUASION_TARGET = "persuasion target"

        @classmethod
        def bribe(cls, n: int) -> str:
            return f"bribed {n}T"

    class Title(Enum):
        CENSOR = "Censor"
        DICTATOR = "Dictator"
        FACTION_LEADER = "faction leader"
        FIELD_CONSUL = "Field Consul"
        HRAO = "HRAO"
        MASTER_OF_HORSE = "Master of Horse"
        ROME_CONSUL = "Rome Consul"
        PRESIDING_MAGISTRATE = "presiding magistrate"
        PRIOR_CONSUL = "prior consul"
        PROCONSUL = "proconsul"

    game = models.ForeignKey(Game, related_name="senators", on_delete=models.CASCADE)
    family_name = models.CharField(max_length=20)
    statesman_name = models.CharField(max_length=60, null=True, blank=True)
    family = models.BooleanField(default=True)
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
    location = models.CharField(max_length=20, default="Rome")

    # Avoid using these directly - use helper methods instead
    status_items = models.JSONField(default=list, blank=True)
    titles = models.JSONField(default=list, blank=True)
    concessions = models.JSONField(default=list, blank=True)
    corrupt_concessions = models.JSONField(default=list, blank=True)

    @property
    def name(self) -> str:
        return self.statesman_name or self.family_name

    @property
    def votes(self) -> int:
        return self.oratory + self.knights

    @property
    def display_name(self) -> str:
        if self.statesman_name:
            return self.statesman_name
        return (
            self.family_name
            if self.generation == 1
            else f"{self.family_name} {roman.toRoman(self.generation)}"
        )

    # Change popularity safely, returning actual change
    def change_popularity(self, change) -> int:
        new_popularity = self.popularity + change
        if new_popularity > 9:
            new_popularity = 9
        if new_popularity < -9:
            new_popularity = -9
        actual_change = new_popularity - self.popularity
        self.popularity = new_popularity
        return actual_change

    # status_items methods

    def add_status_item(self, status: StatusItem) -> None:
        if status.value not in self.status_items:
            self.status_items.append(status.value)

    def remove_status_item(self, status: StatusItem) -> None:
        if status.value in self.status_items:
            self.status_items.remove(status.value)

    def clear_status_items(self) -> None:
        self.status_items = []

    def has_status_item(self, status: StatusItem) -> bool:
        return status.value in self.status_items

    def get_bribe_amount(self) -> Optional[int]:
        for s in self.status_items:
            if s.startswith("bribe"):
                return int(s.split(" ")[1][:-1])
        return None

    def set_bribe_amount(self, amount: Optional[int]):
        self.status_items = [s for s in self.status_items if not s.startswith("bribe")]
        if amount is not None:
            self.status_items.append(Senator.StatusItem.bribe(amount))

    # titles methods

    def add_title(self, title: Title) -> None:
        if title.value not in self.titles:
            self.titles.append(title.value)

    def remove_title(self, title: Title) -> None:
        if title.value in self.titles:
            self.titles.remove(title.value)

    def clear_titles(self) -> None:
        self.titles = []

    def has_title(self, title: Title) -> bool:
        return title.value in self.titles

    # concessions methods

    def add_concession(self, concession: Concession) -> None:
        if concession.value not in self.concessions:
            self.concessions.append(concession.value)

    def remove_concession(self, concession: Concession) -> None:
        if concession.value in self.concessions:
            self.concessions.remove(concession.value)

    def clear_concessions(self) -> None:
        self.concessions = []

    def has_concession(self, concession: Concession) -> bool:
        return concession.value in self.concessions

    def get_concessions(self) -> List[Concession]:
        return [Concession(concession) for concession in self.concessions]

    # corrupt_concessions methods

    def add_corrupt_concession(self, concession: Concession) -> None:
        if concession.value not in self.corrupt_concessions:
            self.corrupt_concessions.append(concession.value)

    def remove_corrupt_concession(self, concession: Concession) -> None:
        if concession.value in self.corrupt_concessions:
            self.corrupt_concessions.remove(concession.value)

    def clear_corrupt_concessions(self) -> None:
        self.corrupt_concessions = []

    def has_corrupt_concession(self, concession: Concession) -> bool:
        return concession.value in self.corrupt_concessions

    def get_corrupt_concessions(self) -> List[Concession]:
        return [Concession(concession) for concession in self.corrupt_concessions]
