from django.utils import timezone
from rorapp.models import Game
from rorapp.functions.websocket_message_helper import create_websocket_message
from rorapp.serializers import GameDetailSerializer


def end_game(game_id: int) -> None:
    game = Game.objects.get(id=game_id)
    game.end_date = timezone.now()
    game.save()
    return [create_websocket_message("game", GameDetailSerializer(game).data)]
