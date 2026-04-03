from django.db import models
from django.core.validators import MinValueValidator

from rorapp.models.game import Game


class War(models.Model):

    class Status(models.TextChoices):
        INACTIVE = "inactive", "inactive"
        IMMINENT = "imminent", "imminent"
        ACTIVE = "active", "active"

    game = models.ForeignKey(Game, related_name="wars", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    series_name = models.CharField(max_length=20, blank=True, null=True)
    index = models.IntegerField(validators=[MinValueValidator(0)])
    land_strength = models.IntegerField(validators=[MinValueValidator(1)])
    fleet_support = models.IntegerField(validators=[MinValueValidator(0)])
    naval_strength = models.IntegerField(validators=[MinValueValidator(0)])
    disaster_numbers = models.JSONField(default=list, blank=True)
    standoff_numbers = models.JSONField(default=list, blank=True)
    spoils = models.IntegerField(validators=[MinValueValidator(0)])
    famine = models.BooleanField(default=False)
    location = models.CharField(max_length=20)

    status = models.CharField(max_length=12, choices=Status.choices)
    unprosecuted = models.BooleanField(default=False)

    # Turn states
    spent_disaster_numbers = models.JSONField(default=list, blank=True)
    spent_standoff_numbers = models.JSONField(default=list, blank=True)
    fought_land_battle = models.BooleanField(default=False)
    fought_naval_battle = models.BooleanField(default=False)

    def reset_turn_states(self):
        self.spent_disaster_numbers = []
        self.spent_standoff_numbers = []
        self.fought_land_battle = False
        self.fought_naval_battle = False

    def is_active_disaster(self, number: int) -> bool:
        return number in self.disaster_numbers and number not in self.spent_disaster_numbers

    def spend_disaster(self, number: int) -> None:
        self.spent_disaster_numbers.append(number)

    def is_active_standoff(self, number: int) -> bool:
        return number in self.standoff_numbers and number not in self.spent_standoff_numbers

    def spend_standoff(self, number: int) -> None:
        self.spent_standoff_numbers.append(number)
