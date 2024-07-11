from django.db import migrations


class Migration(migrations.Migration):
    def remove_new_turn_action_logs(apps, schema_editor):
        ActionLog = apps.get_model("rorapp", "ActionLog")
        ActionLog.objects.filter(type="new_turn").delete()

    dependencies = [
        ("rorapp", "0060_faction_custom_name"),
    ]

    operations = [
        migrations.RunPython(remove_new_turn_action_logs, migrations.RunPython.noop),
    ]
