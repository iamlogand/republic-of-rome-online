# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0039_rename_recently_deployed_or_reinforced_campaign_recently_deployed_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='availableaction',
            old_name='name',
            new_name='base_name',
        ),
        migrations.AddField(
            model_name='availableaction',
            name='variant_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
