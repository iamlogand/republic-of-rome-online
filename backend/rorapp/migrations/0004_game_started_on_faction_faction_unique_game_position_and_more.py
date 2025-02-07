# Generated by Django 5.0.7 on 2025-02-07 18:09

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0003_rename_creation_on_game_created_on'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='started_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Faction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(6)])),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rorapp.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='faction',
            constraint=models.UniqueConstraint(fields=('game', 'position'), name='unique_game_position'),
        ),
        migrations.AddConstraint(
            model_name='faction',
            constraint=models.UniqueConstraint(fields=('game', 'player'), name='unique_game_player'),
        ),
    ]
