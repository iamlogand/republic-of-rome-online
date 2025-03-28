# Generated by Django 5.0.7 on 2025-02-10 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0009_game_turn"),
    ]

    operations = [
        migrations.RenameField(
            model_name="availableaction",
            old_name="type",
            new_name="name",
        ),
        migrations.RemoveField(
            model_name="availableaction",
            name="schema",
        ),
        migrations.RemoveField(
            model_name="faction",
            name="cards",
        ),
        migrations.AddField(
            model_name="faction",
            name="status",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="game",
            name="state_treasury",
            field=models.IntegerField(default=100),
        ),
    ]
