from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0057_province_frontier'),
    ]

    operations = [
        migrations.AddField(
            model_name='fleet',
            name='recently_raised',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='disbanded_fleet_numbers',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='game',
            name='disbanded_legion_numbers',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='legion',
            name='recently_raised',
            field=models.BooleanField(default=False),
        ),
    ]
