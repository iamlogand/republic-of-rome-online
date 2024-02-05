import random
from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration shuffles the order of situations in each game,
    fixing a bug where the order was only partially shuffled.
    """

    def shuffle_situations(apps, schema_editor):
        Situation = apps.get_model("rorapp", "Situation")
        Game = apps.get_model("rorapp", "Game")

        games = Game.objects.all()
        for game in games:
            situations = list(Situation.objects.filter(game=game))
            random.shuffle(situations)
            for i, situation in enumerate(situations):
                situation.index = i
                situation.save()

    dependencies = [
        ("rorapp", "0043_situation_secret"),
    ]

    operations = [
        migrations.RunPython(shuffle_situations, migrations.RunPython.noop),
    ]
