# Generated by Django 4.2.2 on 2023-08-30 07:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0023_senator_influence_senator_knights_senator_loyalty_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Office",
            new_name="Title",
        ),
    ]
