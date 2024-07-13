from django.db import migrations


class Migration(migrations.Migration):
    def change_syrian_war_index(apps, schema_editor):
        """
        Change the Syrian War index from 1 to 0, to reflect that fact that it isn't part of a series.
        """

        # Update the Wars
        War = apps.get_model("rorapp", "War")
        for war in War.objects.filter(name="Syrian"):
            war.index = 0
            war.save()

        # Update the Situations
        Situation = apps.get_model("rorapp", "Situation")
        for situation in Situation.objects.filter(name="Syrian 1"):
            situation.name = "Syrian"
            situation.save()

    dependencies = [
        ("rorapp", "0046_rename_war_situations"),
    ]

    operations = [
        migrations.RunPython(change_syrian_war_index, migrations.RunPython.noop), # type: ignore
    ]
