from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.timezone import now

from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem


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
        CONSULAR_ELECTION = "consular election", "consular election"
        END = "end", "end"
        FACTION_LEADER = "faction leader", "faction leader"
        INITIATIVE_AUCTION = "initiative auction", "initiative auction"
        INITIATIVE_ROLL = "initiative roll", "initiative roll"
        OTHER_BUSINESS = "other business", "other business"
        REDISTRIBUTION = "redistribution", "redistribution"
        RESOLUTION = "resolution", "resolution"
        SPONSOR_GAMES = "sponsor games", "sponsor games"
        START = "start", "start"
        PLAY_STATESMEN_CONCESSIONS = "play statesmen/concessions", "play statesmen/concessions"

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
    unrest = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    current_proposal = models.TextField(max_length=100, blank=True, null=True)
    defeated_proposals = models.JSONField(default=list, blank=True)
    votes_nay = models.IntegerField(default=0)
    votes_yea = models.IntegerField(default=0)
    concessions = models.JSONField(default=list, blank=True)

    @property
    def has_password(self):
        return self.password != ""

    @property
    def status(self):
        if not self.started_on and not self.finished_on:
            return "pending"
        elif not self.finished_on:
            return "active"
        else:
            return "finished"

    @property
    def votes_pending(self: "Game"):
        votes = 0
        for faction in self.factions.all():
            if not faction.has_status_item(FactionStatusItem.DONE):
                for senator in faction.senators.all():
                    votes += senator.votes
        return votes

    # Change unrest safely, returning actual change
    def change_unrest(self, change) -> int:
        new_unrest = self.unrest + change
        if new_unrest < 0:
            new_unrest = 0
        actual_change = new_unrest - self.unrest
        self.unrest = new_unrest
        return actual_change

    # Concession methods

    def add_concession(self, concession: Concession) -> None:
        if concession.value not in self.concessions:
            self.concessions.append(concession.value)

    def remove_concession(self, concession: Concession) -> None:
        if concession.value in self.concessions:
            self.concessions.remove(concession.value)

    def has_concession(self, concession: Concession) -> bool:
        return concession.value in self.concessions
