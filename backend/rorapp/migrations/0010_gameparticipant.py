# Generated by Django 4.1.1 on 2023-05-03 20:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def create_game_participants_for_owners(apps, schema_editor):
    Game = apps.get_model('rorapp', 'Game')
    GameParticipant = apps.get_model('rorapp', 'GameParticipant')

    for game in Game.objects.all():
        game_participant = GameParticipant(user=game.owner, game=game, join_date=game.creation_date)
        game_participant.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rorapp', '0009_alter_game_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('join_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rorapp.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RunPython(create_game_participants_for_owners),
    ]
