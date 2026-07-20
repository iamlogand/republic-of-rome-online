import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0054_rename_schema_to_field_descriptors"),
    ]

    operations = [
        migrations.AddField(
            model_name="combatcalculation",
            name="evil_omens",
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10),
                ],
            ),
        ),
    ]
