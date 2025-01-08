# This migration does not change models, but it does change data in the database.

from django.db import migrations


# Rename notification data "heir_senator" key to "heir_senator"
# In a future version, notifications might be used as a log of events, so it's better to keep the data consistent.
# Any data key that contains a senator ID should be suffixed with "senator".
def update_notification_data(apps, schema_editor):
    Notification = apps.get_model("rorapp", "Notification")

    face_mortality_notifications = Notification.objects.filter(type="face_mortality")

    for notification in face_mortality_notifications:
        notification.data["heir_senator"] = notification.data["heir"]
        del notification.data["heir"]
        notification.save()


class Migration(migrations.Migration):
    dependencies = [
        ("rorapp", "0031_senator_rank_and_faction_rank"),
    ]

    operations = [
        migrations.RunPython(update_notification_data, migrations.RunPython.noop),
    ]
