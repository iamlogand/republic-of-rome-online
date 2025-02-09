from django.utils.timezone import now

from rorapp.models import Faction, Game
from rorapp.serializers import FactionSerializer, SimpleGameSerializer


def get_game_state(game_id: int):
    game = Game.objects.get(id=game_id)
    factions = Faction.objects.filter(game=game_id)

    game_data = SimpleGameSerializer(game).data
    factions_data = FactionSerializer(factions, many=True).data

    timestamp = now().isoformat()

    return {
        "timestamp": timestamp,
        "game": game_data,
        "factions": factions_data,
    }
