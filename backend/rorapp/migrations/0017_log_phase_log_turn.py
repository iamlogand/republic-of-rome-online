# Generated by Django 5.0.7 on 2025-02-23 15:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0016_senator_generation_alter_game_phase"),
    ]

    operations = [
        migrations.AddField(
            model_name="log",
            name="phase",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Initial", "Initial"),
                    ("Mortality", "Mortality"),
                    ("Revenue", "Revenue"),
                    ("Forum", "Forum"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="log",
            name="turn",
            field=models.IntegerField(
                default=1, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
    ]
