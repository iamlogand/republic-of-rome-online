from enum import Enum
from typing import Union
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from rorapp.models.game import Game


class Faction(models.Model):

    class StatusItem(Enum):
        DONE = "Done"
        CURRENT_INITIATIVE = "Current initiative"

        @classmethod
        def initiative(cls, x: int) -> str:
            """Dynamically generates an initiative status."""
            return f"Initiative {x}"

    class Card(Enum):
        TRIBUNE = "Tribune"

    game = models.ForeignKey(Game, related_name="factions", on_delete=models.CASCADE)
    player = models.ForeignKey(User, related_name="factions", on_delete=models.CASCADE)
    position = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    treasury = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    cards = models.JSONField(default=list, blank=True)
    status_items = models.JSONField(default=list, blank=True)

    @property
    def card_count(self) -> int:
        return len(self.cards) if self.cards else 0

    @property
    def display_name(self) -> str:
        return f"Faction {self.position}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "position"], name="unique_game_position"
            ),
            models.UniqueConstraint(
                fields=["game", "player"], name="unique_game_player"
            ),
        ]

    def add_status_item(self, status: Union[StatusItem, str]) -> None:
        status_value = status.value if isinstance(status, self.StatusItem) else status
        if status_value not in self.status_items:
            self.status_items.append(status_value)
            self.save()

    def remove_status_item(self, status: Union[StatusItem, str]) -> None:
        status_value = status.value if isinstance(status, self.StatusItem) else status
        if status_value in self.status_items:
            self.status_items.remove(status_value)
            self.save()

    def has_status_item(self, status: Union[StatusItem, str]) -> bool:
        status_value = status.value if isinstance(status, self.StatusItem) else status
        return status_value in self.status_items

    def add_card(self, card: Card) -> None:
        if card.value not in self.cards:
            self.cards.append(card.value)
            self.save()

    def remove_card(self, card: Card) -> None:
        if card.value in self.cards:
            self.cards.remove(card.value)
            self.save()

    def has_card(self, card: Card) -> bool:
        return card.value in self.cards
