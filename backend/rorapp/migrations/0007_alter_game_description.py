# Generated by Django 4.1.1 on 2023-03-19 17:55
# Edited by Logan on 2023-03-19 17:58: added the shorten_description operation

from django.db import migrations, models
from django.db.migrations.operations import RunPython


def shorten_description(apps, schema_editor):
    Game = apps.get_model("rorapp", "game")
    for game in Game.objects.all():
        game.description = game.description[:1000]
        game.save()


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0006_alter_game_start_date"),
    ]

    operations = [
        RunPython(shorten_description),
        migrations.AlterField(
            model_name="game",
            name="description",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
