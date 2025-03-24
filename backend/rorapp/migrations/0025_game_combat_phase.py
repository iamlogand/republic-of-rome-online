from django.db import migrations, models


class Migration(migrations.Migration):

    def forward_migrate_games(apps, schema_editor):
        Game = apps.get_model("rorapp", "Game")
        games = Game.objects.filter(phase="Military")
        for game in games:
            game.phase = "Combat"
            game.save()

    def backward_migrate_games(apps, schema_editor):
        Game = apps.get_model("rorapp", "Game")
        games = Game.objects.filter(phase="Combat")
        for game in games:
            game.phase = "Military"
            game.save()

    dependencies = [
        ("rorapp", "0024_war_unprosecuted_alter_game_phase_alter_log_phase_and_more"),
    ]

    operations = [
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
                    ("Combat", "Combat"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.RunPython(forward_migrate_games, backward_migrate_games),  # type: ignore
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
                    ("Combat", "Combat"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
