# Generated by Django 5.0.7 on 2025-02-10 16:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0007_faction_cards_faction_treasury"),
    ]

    operations = [
        migrations.CreateModel(
            name="AvailableAction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("type", models.CharField(max_length=50)),
                ("schema", models.JSONField(blank=True, null=True)),
                (
                    "faction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="factions",
                        to="rorapp.faction",
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="actions",
                        to="rorapp.game",
                    ),
                ),
            ],
        ),
    ]
