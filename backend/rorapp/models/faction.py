from enum import Enum
from typing import Optional, Union
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.models.game import Game


class Faction(models.Model):

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
                fields=["game", "position"], name="unique_faction_game_position"
            ),
            models.UniqueConstraint(
                fields=["game", "player"], name="unique_faction_game_player"
            ),
        ]

    INITIATIVE_INDICES = [1, 2, 3, 4, 5, 6]

    # Status item helpers

    def add_status_item(self, status: Union[FactionStatusItem, str]) -> None:
        status_value = status.value if isinstance(status, FactionStatusItem) else status
        if status_value not in self.status_items:
            self.status_items.append(status_value)
            self.save()

    def remove_status_item(self, status: Union[FactionStatusItem, str]) -> None:
        status_value = status.value if isinstance(status, FactionStatusItem) else status
        if status_value in self.status_items:
            self.status_items.remove(status_value)
            self.save()

    def has_status_item(self, status: Union[FactionStatusItem, str]) -> bool:
        status_value = status.value if isinstance(status, FactionStatusItem) else status
        return status_value in self.status_items

    # Bid amount status item helpers

    def get_bid_amount(self) -> Optional[int]:
        for status in self.status_items:
            if status.startswith("Bid"):
                return int(status.split(" ")[1][:-1])
        return None

    def set_bid_amount(self, amount: Optional[int]):
        self.status_items = [s for s in self.status_items if not s.startswith("Bid")]
        if amount:
            self.status_items.append(FactionStatusItem.bid(amount))
        self.save()
