from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0052_add_unavailable_proposals_to_game"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="assassination_roll_modifier",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="game",
            name="assassination_roll_result",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="game",
            name="bodyguard_rerolls_remaining",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="game",
            name="interrupted_sub_phase",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
        migrations.AlterField(
            model_name="game",
            name="sub_phase",
            field=models.CharField(
                blank=True,
                choices=[
                    ("attract knight", "attract knight"),
                    ("censor election", "censor election"),
                    ("consular election", "consular election"),
                    ("dictator appointment", "dictator appointment"),
                    ("dictator election", "dictator election"),
                    ("end", "end"),
                    ("faction leader", "faction leader"),
                    ("master of horse appointment", "master of horse appointment"),
                    ("initiative auction", "initiative auction"),
                    ("initiative roll", "initiative roll"),
                    ("other business", "other business"),
                    ("prosecution", "prosecution"),
                    ("redistribution", "redistribution"),
                    ("resolution", "resolution"),
                    ("sponsor games", "sponsor games"),
                    ("start", "start"),
                    ("card trading", "card trading"),
                    ("play statesmen/concessions", "play statesmen/concessions"),
                    ("persuasion attempt", "persuasion attempt"),
                    ("persuasion counter-bribe", "persuasion counter-bribe"),
                    ("persuasion decision", "persuasion decision"),
                    ("putting Rome in order", "putting Rome in order"),
                    ("era ends", "era ends"),
                    ("state of the Republic speech", "state of the Republic speech"),
                    ("assassination resolution", "assassination resolution"),
                ],
                max_length=30,
                null=True,
            ),
        ),
    ]
