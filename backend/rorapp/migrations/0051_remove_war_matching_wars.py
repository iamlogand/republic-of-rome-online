# Generated by Django 4.2.3 on 2024-02-24 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0050_enemyleader'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='war',
            name='matching_wars',
        ),
    ]
