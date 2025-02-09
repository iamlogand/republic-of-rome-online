from django.utils.timezone import now

from rorapp.models import Faction, Game, Senator
from rorapp.serializers import (
    FactionSerializer,
    SenatorSerializer,
    SimpleGameSerializer,
)


def get_game_state(game_id: int):
    game = Game.objects.get(id=game_id)
    factions = Faction.objects.filter(game=game_id)
    senators = Senator.objects.filter(game=game_id)

    game_data = SimpleGameSerializer(game).data
    factions_data = FactionSerializer(factions, many=True).data
    senators_data = SenatorSerializer(senators, many=True).data

    timestamp = now().isoformat()

    return {
        "timestamp": timestamp,
        "game": game_data,
        "factions": factions_data,
        "senators": senators_data,
    }
