from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.timezone import now


class Game(models.Model):
    name = models.CharField(max_length=100, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=now)
    started_on = models.DateTimeField(blank=True, null=True)
    finished_on = models.DateTimeField(blank=True, null=True)
    step = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    turn = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    phase = models.CharField(max_length=20, blank=True, null=True)
    sub_phase = models.CharField(max_length=20, blank=True, null=True)
    state_treasury = models.IntegerField(default=100)

    @property
    def status(self):
        if not self.started_on and not self.finished_on:
            return "Pending"
        elif not self.finished_on:
            return "Active"
        else:
            return "Finished"
        
    def increment_step(self):
        self.step = self.step + 1
        self.save()