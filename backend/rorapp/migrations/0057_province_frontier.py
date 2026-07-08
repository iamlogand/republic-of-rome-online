import json
import os

from django.conf import settings
from django.db import migrations, models


def backfill_province_frontier(apps, schema_editor):
    Province = apps.get_model("rorapp", "Province")
    path = os.path.join(settings.BASE_DIR, "rorapp", "data", "province.json")
    with open(path, "r") as f:
        provinces = json.load(f)

    for province in Province.objects.all():
        data = provinces.get(province.name, {})
        province.frontier = data.get("frontier", False)
        province.save(update_fields=["frontier"])


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0056_province"),
    ]

    operations = [
        migrations.AddField(
            model_name="province",
            name="frontier",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(backfill_province_frontier, migrations.RunPython.noop),
    ]
