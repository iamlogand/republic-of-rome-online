# Generated by Django 4.2.2 on 2023-08-18 19:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0017_phase_index"),
    ]

    operations = [
        migrations.AlterField(
            model_name="completedaction",
            name="type",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="potentialaction",
            name="type",
            field=models.CharField(max_length=50),
        ),
    ]
