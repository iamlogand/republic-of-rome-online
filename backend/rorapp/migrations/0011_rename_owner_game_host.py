# Generated by Django 4.1.1 on 2023-05-22 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0010_gameparticipant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='owner',
            new_name='host',
        ),
    ]
