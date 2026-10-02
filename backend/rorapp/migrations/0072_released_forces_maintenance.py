from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0071_rebel_forces_release'),
    ]

    operations = [
        migrations.AddField(
            model_name='legion',
            name='released_by_rebel',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='game',
            name='sub_phase',
            field=models.CharField(blank=True, choices=[('attract knight', 'attract knight'), ('censor election', 'censor election'), ('consular election', 'consular election'), ('dictator appointment', 'dictator appointment'), ('dictator election', 'dictator election'), ('end', 'end'), ('faction leader', 'faction leader'), ('master of horse appointment', 'master of horse appointment'), ('new alliance', 'new alliance'), ('initiative auction', 'initiative auction'), ('initiative roll', 'initiative roll'), ('other business', 'other business'), ('prosecution', 'prosecution'), ('redistribution', 'redistribution'), ('repopulation', 'repopulation'), ('resolution', 'resolution'), ('revolt declaration', 'revolt declaration'), ('sponsor games', 'sponsor games'), ('start', 'start'), ('card trading', 'card trading'), ('play statesmen/concessions', 'play statesmen/concessions'), ('persuasion attempt', 'persuasion attempt'), ('persuasion counter-bribe', 'persuasion counter-bribe'), ('persuasion decision', 'persuasion decision'), ('putting Rome in order', 'putting Rome in order'), ('released legions disbandment', 'released legions disbandment'), ('rebel legions release', 'rebel legions release'), ('era ends', 'era ends'), ('state of the Republic speech', 'state of the Republic speech'), ('assassination resolution', 'assassination resolution'), ('special major prosecution', 'special major prosecution'), ('storm at sea', 'storm at sea')], max_length=30, null=True),
        ),
    ]
