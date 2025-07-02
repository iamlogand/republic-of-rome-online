from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.timezone import now


class Game(models.Model):

    class Phase(models.TextChoices):
        INITIAL = "Initial", "Initial"
        MORTALITY = "Mortality", "Mortality"
        REVENUE = "Revenue", "Revenue"
        FORUM = "Forum", "Forum"
        POPULATION = "Population", "Population"
        SENATE = "Senate", "Senate"
        COMBAT = "Combat", "Combat"

    class SubPhase(models.TextChoices):
        ATTRACT_KNIGHT = "Attract knight", "Attract knight"
        CONSULAR_ELECTION = "Consular election", "Consular election"
        END = "End", "End"
        FACTION_LEADER = "Faction leader", "Faction leader"
        INITIATIVE_AUCTION = "Initiative auction", "Initiative auction"
        INITIATIVE_ROLL = "Initiative roll", "Initiative roll"
        REDISTRIBUTION = "Redistribution", "Redistribution"
        SPONSOR_GAMES = "Sponsor games", "Sponsor games"
        START = "Start", "Start"

    name = models.CharField(max_length=100, unique=True)
    host = models.ForeignKey(User, related_name="games", on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=now)
    started_on = models.DateTimeField(blank=True, null=True)
    finished_on = models.DateTimeField(blank=True, null=True)
    step = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    turn = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    phase = models.CharField(
        max_length=20, choices=Phase.choices, blank=True, null=True
    )
    sub_phase = models.CharField(
        max_length=20, choices=SubPhase.choices, blank=True, null=True
    )
    state_treasury = models.IntegerField(default=100)
    deck = models.JSONField(default=list, blank=True)
    unrest = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    current_proposal = models.TextField(max_length=100, blank=True, null=True)
    defeated_proposals = models.JSONField(default=list, blank=True)
    votes_nay = models.IntegerField(default=0)
    votes_yea = models.IntegerField(default=0)

    @property
    def status(self):
        if not self.started_on and not self.finished_on:
            return "Pending"
        elif not self.finished_on:
            return "Active"
        else:
            return "Finished"

    @property
    def votes_pending(self: "Game"):
        # Faction is imported here to avoid circular import
        from rorapp.models.faction import Faction

        votes = 0
        for faction in self.factions.all():
            if not faction.has_status_item(Faction.StatusItem.DONE):
                for senator in faction.senators.all():
                    votes += senator.votes
        return votes
