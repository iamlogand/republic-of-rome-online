from django.db import migrations


class Migration(migrations.Migration):
    def rename_war_situations(apps, schema_editor):
        """
        Reformat war situation names. E.g. "1st Punic War" becomes "Punic 1".
        """

        Situation = apps.get_model("rorapp", "Situation")
        war_situations = Situation.objects.filter(type="war")
        for war_situation in war_situations:
            war_situation_name_items = war_situation.name.split(" ")
            if len(war_situation_name_items) == 3:
                index_with_suffix, name, _ = war_situation_name_items
                index = index_with_suffix[0]
                war_situation.name = f"{name} {index}"
                war_situation.save()

    dependencies = [
        ("rorapp", "0045_war"),
    ]

    operations = [
        migrations.RunPython(rename_war_situations, migrations.RunPython.noop), # type: ignore
    ]
