import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0057_province_frontier"),
    ]

    operations = [
        migrations.AlterField(
            model_name="legion",
            name="allegiance",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="legions_in_allegiance",
                to="rorapp.senator",
            ),
        ),
    ]
