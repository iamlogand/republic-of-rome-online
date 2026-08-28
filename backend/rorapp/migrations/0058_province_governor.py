import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0057_province_frontier"),
    ]

    operations = [
        migrations.AddField(
            model_name="province",
            name="elected_this_turn",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="province",
            name="governor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="governed_provinces",
                to="rorapp.senator",
            ),
        ),
        migrations.AddField(
            model_name="province",
            name="term",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(3),
                ],
            ),
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
                    ("governor election", "governor election"),
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
