from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0051_combatcalculation_is_dictator_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="unavailable_proposals",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
