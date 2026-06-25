from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0053_assassination_fields"),
    ]

    operations = [
        migrations.RenameField(
            model_name="availableaction",
            old_name="schema",
            new_name="field_descriptors",
        ),
    ]
