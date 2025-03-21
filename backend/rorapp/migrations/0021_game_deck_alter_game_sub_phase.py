# Generated by Django 5.0.7 on 2025-03-17 19:41
import random
from django.db import migrations, models


class Migration(migrations.Migration):

    def add_wars_to_decks(apps, schema_editor):
        Game = apps.get_model("rorapp", "Game")
        games = Game.objects.all()
        for game in games:
            new_deck = [
                "war:1st Punic War",
                "war:2nd Punic War",
                "war:1st Illyrian War",
                "war:2nd Illyrian War",
                "war:1st Gallic War",
                "war:1st Macedonian War",
                "war:2nd Macedonian War",
                "war:Syrian War",
            ]
            random.shuffle(new_deck)
            game.deck = new_deck
            game.save()

    dependencies = [
        ("rorapp", "0020_availableaction_context"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="deck",
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name="game",
            name="sub_phase",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Initiative roll", "Initiative roll"),
                    ("Attract knight", "Attract knight"),
                    ("End", "End"),
                    ("Faction leader", "Faction leader"),
                    ("Initiative auction", "Initiative auction"),
                    ("Redistribution", "Redistribution"),
                    ("Sponsor games", "Sponsor games"),
                    ("Start", "Start"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.RunPython(add_wars_to_decks, migrations.RunPython.noop),  # type: ignore
    ]
