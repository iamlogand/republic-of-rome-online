# Generated by Django 5.0.7 on 2025-03-22 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    def forward_migrate_unprosecuted_wars(apps, schema_editor):
        War = apps.get_model("rorapp", "War")
        unprosecuted_wars = War.objects.filter(status="Unprosecuted")
        for war in unprosecuted_wars:
            war.status = "Active"
            war.unprosecuted = True
            war.save()

    def backward_migrate_unprosecuted_wars(apps, schema_editor):
        War = apps.get_model("rorapp", "War")
        unprosecuted_wars = War.objects.filter(unprosecuted=True)
        for war in unprosecuted_wars:
            war.status = "Unprosecuted"
            war.save()

    dependencies = [
        ("rorapp", "0023_game_unrest"),
    ]

    operations = [
        migrations.AddField(
            model_name="war",
            name="unprosecuted",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="game",
            name="phase",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Initial", "Initial"),
                    ("Mortality", "Mortality"),
                    ("Revenue", "Revenue"),
                    ("Forum", "Forum"),
                    ("Population", "Population"),
                    ("Military", "Military"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="log",
            name="phase",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Initial", "Initial"),
                    ("Mortality", "Mortality"),
                    ("Revenue", "Revenue"),
                    ("Forum", "Forum"),
                    ("Population", "Population"),
                    ("Military", "Military"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.RunPython(forward_migrate_unprosecuted_wars, backward_migrate_unprosecuted_wars),  # type: ignore
        migrations.AlterField(
            model_name="war",
            name="status",
            field=models.CharField(
                choices=[
                    ("Inactive", "Inactive"),
                    ("Imminent", "Imminent"),
                    ("Active", "Active"),
                    ("Defeated", "Defeated"),
                ],
                max_length=12,
            ),
        ),
    ]
