# Generated by Django 4.2.2 on 2023-11-13 20:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0038_potentialaction_completed'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PotentialAction',
            new_name='Action',
        ),
        migrations.DeleteModel(
            name='CompletedAction',
        ),
    ]
