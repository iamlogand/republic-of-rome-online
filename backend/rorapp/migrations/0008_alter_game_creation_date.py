# Generated by Django 4.1.1 on 2023-03-19 19:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0007_alter_game_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="creation_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
