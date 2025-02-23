from typing import Dict, List, Tuple
from django.utils.timezone import now

from rorapp.models import Faction, Game, Log, Senator
from rorapp.models.available_action import AvailableAction
from rorapp.serializers import (
    AvailableActionSerializer,
    FactionPublicSerializer,
    FactionPrivateSerializer,
    SenatorSerializer,
    SimpleGameSerializer,
)
from rorapp.serializers.log import LogSerializer


def get_public_game_state(game_id: int) -> Tuple[Dict, List[int]]:
    try:
        game = Game.objects.get(id=game_id)
    except:
        return ({}, [])  # Game has been deleted

    factions = Faction.objects.filter(game=game_id)
    senators = Senator.objects.filter(game=game_id)
    logs = Log.objects.filter(game=game_id)

    game_data = SimpleGameSerializer(game).data
    factions_data = FactionPublicSerializer(factions, many=True).data
    senators_data = SenatorSerializer(senators, many=True).data
    log_data = LogSerializer(logs, many=True).data

    timestamp = now().isoformat()

    player_ids = [f.player.id for f in factions]

    return (
        {
            "type": "public game state",
            "timestamp": timestamp,
            "game": game_data,
            "factions": factions_data,
            "senators": senators_data,
            "logs": log_data,
        },
        player_ids,
    )


def get_private_game_state(game_id: int, user_id: int) -> Dict:
    faction = Faction.objects.get(game=game_id, player=user_id)
    available_actions = AvailableAction.objects.filter(faction=faction.id)

    faction_data = FactionPrivateSerializer(faction).data
    available_actions_data = AvailableActionSerializer(
        available_actions, many=True
    ).data

    timestamp = now().isoformat()

    return {
        "type": "private game state",
        "timestamp": timestamp,
        "available_actions": available_actions_data,
        "faction": faction_data,
    }
