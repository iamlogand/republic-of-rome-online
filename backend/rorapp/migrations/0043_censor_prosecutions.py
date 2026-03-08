from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0042_lowercase_enum_values"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="prosecutions_remaining",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="senator",
            name="corrupt_concessions",
            field=models.JSONField(blank=True, default=list),
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
                    ("end", "end"),
                    ("faction leader", "faction leader"),
                    ("initiative auction", "initiative auction"),
                    ("initiative roll", "initiative roll"),
                    ("other business", "other business"),
                    ("prosecution", "prosecution"),
                    ("redistribution", "redistribution"),
                    ("resolution", "resolution"),
                    ("sponsor games", "sponsor games"),
                    ("start", "start"),
                    ("play statesmen/concessions", "play statesmen/concessions"),
                ],
                max_length=30,
                null=True,
            ),
        ),
    ]
