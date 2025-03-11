# Generated by Django 5.0.7 on 2025-03-05 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0018_availableaction_position_alter_game_sub_phase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='sub_phase',
            field=models.CharField(blank=True, choices=[('Attract knight', 'Attract knight'), ('End', 'End'), ('Faction leader', 'Faction leader'), ('Initiative auction', 'Initiative auction'), ('Redistribution', 'Redistribution'), ('Sponsor games', 'Sponsor games'), ('Start', 'Start')], max_length=20, null=True),
        ),
    ]
