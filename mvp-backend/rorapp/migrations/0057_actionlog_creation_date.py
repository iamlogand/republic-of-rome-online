# Generated by Django 4.2.3 on 2024-03-08 00:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0056_alter_phase_name_alter_game_end_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="actionlog",
            name="creation_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
