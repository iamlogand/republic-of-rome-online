# Generated by Django 4.2.2 on 2023-08-21 07:11

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rorapp", "0020_alter_completedaction_parameters_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="GameParticipant",
            new_name="Player",
        ),
    ]
