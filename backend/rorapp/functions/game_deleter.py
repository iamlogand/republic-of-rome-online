from rorapp.serializers.game import Game


def delete_all_games():
    Game.objects.all().delete()
