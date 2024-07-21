from django.db import migrations


def add_prior_consul_titles(apps, schema_editor):
    Senator = apps.get_model("rorapp", "Senator")
    Title = apps.get_model("rorapp", "Title")
    temporary_rome_consul_titles = Title.objects.filter(name="Temporary Rome Consul")
    for title in temporary_rome_consul_titles:
        senator = Senator.objects.get(id=title.senator.id)
        prior_consul_title_exists = Title.objects.filter(
            name="Prior Consul", senator=senator
        ).exists()
        if not prior_consul_title_exists:
            prior_consul_title = Title.objects.create(
                name="Prior Consul",
                senator=senator,
                start_step=title.start_step,
                end_step=title.end_step,
            )
            prior_consul_title.save()


def remove_prior_consul_titles(apps, schema_editor):
    Title = apps.get_model("rorapp", "Title")
    prior_consul_titles = Title.objects.filter(name="Prior Consul")
    prior_consul_titles.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0041_select_faction_leader"),
    ]

    operations = [
        migrations.RunPython(add_prior_consul_titles, remove_prior_consul_titles),
    ]
