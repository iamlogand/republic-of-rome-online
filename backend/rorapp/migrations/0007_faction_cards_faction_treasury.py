# Generated by Django 5.0.7 on 2025-02-10 13:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "rorapp",
            "0006_game_finished_on_game_phase_game_step_game_sub_phase_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="faction",
            name="cards",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="faction",
            name="treasury",
            field=models.IntegerField(
                default=0, validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
    ]
