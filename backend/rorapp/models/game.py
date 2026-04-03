from typing import List, Optional

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.timezone import now

from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect


class Game(models.Model):

    class Phase(models.TextChoices):
        INITIAL = "initial", "initial"
        MORTALITY = "mortality", "mortality"
        REVENUE = "revenue", "revenue"
        FORUM = "forum", "forum"
        POPULATION = "population", "population"
        SENATE = "senate", "senate"
        COMBAT = "combat", "combat"
        REVOLUTION = "revolution", "revolution"

    class SubPhase(models.TextChoices):
        ATTRACT_KNIGHT = "attract knight", "attract knight"
        CENSOR_ELECTION = "censor election", "censor election"
        CONSULAR_ELECTION = "consular election", "consular election"
        END = "end", "end"
        FACTION_LEADER = "faction leader", "faction leader"
        INITIATIVE_AUCTION = "initiative auction", "initiative auction"
        INITIATIVE_ROLL = "initiative roll", "initiative roll"
        OTHER_BUSINESS = "other business", "other business"
        PROSECUTION = "prosecution", "prosecution"
        REDISTRIBUTION = "redistribution", "redistribution"
        RESOLUTION = "resolution", "resolution"
        SPONSOR_GAMES = "sponsor games", "sponsor games"
        START = "start", "start"
        CARD_TRADING = "card trading", "card trading"
        PLAY_STATESMEN_CONCESSIONS = (
            "play statesmen/concessions",
            "play statesmen/concessions",
        )
        PUTTING_ROME_IN_ORDER = "putting Rome in order", "putting Rome in order"
        ERA_ENDS = "era ends", "era ends"
        STATE_OF_REPUBLIC_SPEECH = (
            "state of the Republic speech",
            "state of the Republic speech",
        )

    name = models.CharField(max_length=100, unique=True)
    host = models.ForeignKey(User, related_name="games", on_delete=models.CASCADE)
    password = models.CharField(default="", max_length=100, blank=True, null=True)
    created_on = models.DateTimeField(default=now)
    started_on = models.DateTimeField(blank=True, null=True)
    finished_on = models.DateTimeField(blank=True, null=True)
    step = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    turn = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    phase = models.CharField(
        max_length=10, choices=Phase.choices, blank=True, null=True
    )
    sub_phase = models.CharField(
        max_length=30, choices=SubPhase.choices, blank=True, null=True
    )
    state_treasury = models.IntegerField(default=100)
    deck = models.JSONField(default=list, blank=True)
    era_ends = models.BooleanField(default=False)
    unrest = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    current_proposal = models.TextField(max_length=100, blank=True, null=True)
    defeated_proposals = models.JSONField(default=list, blank=True)
    votes_nay = models.IntegerField(default=0)
    votes_yea = models.IntegerField(default=0)
    concessions = models.JSONField(default=list, blank=True)
    prosecutions_remaining = models.IntegerField(default=0)
    effects = models.JSONField(default=list, blank=True)

    @property
    def has_password(self) -> bool:
        return self.password != ""

    @property
    def status(self) -> str:
        if not self.started_on and not self.finished_on:
            return "pending"
        elif not self.finished_on:
            return "active"
        else:
            return "finished"

    @property
    def votes_pending(self: "Game") -> int:
        votes = 0
        for faction in self.factions.all():
            if not faction.has_status_item(FactionStatusItem.DONE):
                for senator in faction.senators.all():
                    votes += senator.votes
        return votes

    @property
    def deck_count(self: "Game") -> int:
        return len(self.deck)

    @property
    def famine_severity(self: "Game") -> int:
        return self.wars.filter(famine=True).count()

    @property
    def unprosecuted_wars(self: "Game") -> int:
        return self.wars.filter(unprosecuted=True).count()

    @property
    def available_concessions(self) -> List[str]:
        return [
            concession
            for concession in self.concessions
            if not any(
                f"Award the {concession} concession" in proposal
                for proposal in self.defeated_proposals
            )
        ]

    # Change unrest safely, returning actual change
    def change_unrest(self, change) -> int:
        new_unrest = self.unrest + change
        if new_unrest < 0:
            new_unrest = 0
        actual_change = new_unrest - self.unrest
        self.unrest = new_unrest
        return actual_change

    # Deck methods

    def draw_card(self) -> Optional[str]:
        if not self.deck:
            return None
        card = self.deck[0]
        self.deck = self.deck[1:]
        return card

    # concessions methods

    def add_concession(self, concession: Concession) -> None:
        if concession.value not in self.concessions:
            self.concessions.append(concession.value)

    def remove_concession(self, concession: Concession) -> None:
        if concession.value in self.concessions:
            self.concessions.remove(concession.value)

    def has_concession(self, concession: Concession) -> bool:
        return concession.value in self.concessions

    # effects methods

    def add_effect(self, effect: GameEffect) -> None:
        self.effects.append(effect.value)

    def remove_effect(self, effect: GameEffect) -> None:
        if effect.value in self.effects:
            self.effects.remove(effect.value)

    def clear_effects(self) -> None:
        self.effects = []

    def has_effect(self, effect: GameEffect) -> bool:
        return effect.value in self.effects

    def count_effect(self, effect: GameEffect) -> int:
        return self.effects.count(effect.value)

    # defeated_proposals methods

    def add_defeated_proposal(self, proposal: str) -> None:
        self.defeated_proposals.append(proposal)

    def has_defeated_proposal(self, proposal: str) -> bool:
        return proposal in self.defeated_proposals

    def clear_defeated_proposals(self) -> None:
        self.defeated_proposals = []
