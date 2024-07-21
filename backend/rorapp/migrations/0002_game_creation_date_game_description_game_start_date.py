# Generated by Django 4.1.1 on 2023-03-13 19:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="creation_date",
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="description",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="start_date",
            field=models.DateField(null=True),
        ),
    ]
