from django.db import migrations


class Migration(migrations.Migration):
    def rename_actions(apps, schema_editor):
        ActionLog = apps.get_model("rorapp", "ActionLog")
        select_faction_leader_action_logs = ActionLog.objects.filter(
            type="select_faction_leader"
        )
        for action_log in select_faction_leader_action_logs:
            action_log.type = "new_faction_leader"
            action_log.save()
        face_mortality_action_logs = ActionLog.objects.filter(type="face_mortality")
        for action_log in face_mortality_action_logs:
            action_log.type = "mortality"
            action_log.save()

    dependencies = [
        ("rorapp", "0057_actionlog_creation_date"),
    ]

    operations = [
        migrations.RunPython(rename_actions, migrations.RunPython.noop),  # type: ignore
    ]
