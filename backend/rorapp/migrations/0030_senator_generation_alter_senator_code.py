# Generated by Django 4.2.2 on 2023-09-12 18:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0029_senator_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="senator",
            name="generation",
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="senator",
            name="code",
            field=models.IntegerField(),
        ),
    ]
