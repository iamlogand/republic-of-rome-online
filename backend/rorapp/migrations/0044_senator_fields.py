from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0043_censor_prosecutions"),
    ]

    operations = [
        migrations.RenameField(
            model_name="senator",
            old_name="name",
            new_name="family_name",
        ),
        migrations.AddField(
            model_name="senator",
            name="family",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="senator",
            name="statesman_name",
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
