from django.db import migrations


def increase_influence(apps, schema_editor):
    Title = apps.get_model("rorapp", "Title")
    Senator = apps.get_model("rorapp", "Senator")
    for title in Title.objects.filter(name="Temporary Rome Consul"):
        senator = Senator.objects.get(id=title.senator.id)
        senator.influence += 5
        senator.save()


def decrease_influence(apps, schema_editor):
    Title = apps.get_model("rorapp", "Title")
    Senator = apps.get_model("rorapp", "Senator")
    for title in Title.objects.filter(name="Temporary Rome Consul"):
        senator = Senator.objects.get(id=title.senator.id)
        senator.influence -= 5
        senator.save()


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0039_rename_potentialaction_action_delete_completedaction"),
    ]

    operations = [
        migrations.RunPython(increase_influence, decrease_influence),
    ]
