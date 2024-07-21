# Generated by Django 4.2.2 on 2023-08-31 06:00
# Edited by Logan on 2023-08-31: added the update_titles operation

from django.db import migrations, models


# Set all existing titles to be major offices
def update_titles(apps, schema_editor):
    Title = apps.get_model("rorapp", "Title")

    for title in Title.objects.all():
        title.major_office = True
        title.save()


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0024_rename_office_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="title",
            name="major_office",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(update_titles, migrations.RunPython.noop),
    ]
