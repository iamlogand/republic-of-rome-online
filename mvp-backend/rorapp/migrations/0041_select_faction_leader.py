from django.db import migrations


def add_potential_faction_leaders(apps, schema_editor):
    Action = apps.get_model("rorapp", "Action")
    Faction = apps.get_model("rorapp", "Faction")
    Senator = apps.get_model("rorapp", "Senator")
    for action in Action.objects.filter(type="select_faction_leader", completed=False):
        faction = Faction.objects.get(id=action.faction.id)
        senators = Senator.objects.filter(faction=faction, death_step__isnull=True)
        senator_id_list = [senator.id for senator in senators]
        action.parameters = senator_id_list
        action.save()


def remove_potential_faction_leaders(apps, schema_editor):
    Action = apps.get_model("rorapp", "Action")
    for action in Action.objects.filter(type="select_faction_leader", completed=False):
        action.parameters = None
        action.save()


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0040_temp_rome_consul_influence"),
    ]

    operations = [
        migrations.RunPython(
            add_potential_faction_leaders, remove_potential_faction_leaders
        ),
    ]
