from django.db import migrations, models


def migrate_pending_assassination_rolls(apps, schema_editor):
    Game = apps.get_model("rorapp", "Game")
    Game.objects.filter(assassination_roll_result=0).update(
        assassination_roll_result=None
    )


def restore_pending_assassination_rolls(apps, schema_editor):
    Game = apps.get_model("rorapp", "Game")
    Game.objects.filter(assassination_roll_result__isnull=True).update(
        assassination_roll_result=0
    )


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0071_game_enemy_leader_dies_sub_phase"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="assassination_roll_result",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.RunPython(
            migrate_pending_assassination_rolls,
            restore_pending_assassination_rolls,
        ),
    ]
