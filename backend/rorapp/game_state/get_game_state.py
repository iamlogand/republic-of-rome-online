from typing import Dict, List, Tuple
from django.utils.timezone import now

from rorapp.models import Campaign, Faction, Fleet, Game, Legion, Log, Senator, War
from rorapp.models.available_action import AvailableAction
from rorapp.serializers import (
    AvailableActionSerializer,
    CampaignSerializer,
    FactionPublicSerializer,
    FactionPrivateSerializer,
    FleetSerializer,
    LegionSerializer,
    LogSerializer,
    SenatorSerializer,
    SimpleGameSerializer,
    WarSerializer,
)


def get_public_game_state(game_id: int) -> Tuple[Dict, List[int]]:
    try:
        game = Game.objects.get(id=game_id)
    except:
        return ({}, [])  # Game has been deleted

    campaigns = Campaign.objects.filter(game=game_id)
    factions = Faction.objects.filter(game=game_id)
    fleets = Fleet.objects.filter(game=game_id)
    legions = Legion.objects.filter(game=game_id)
    logs = Log.objects.filter(game=game_id)
    senators = Senator.objects.filter(game=game_id)
    wars = War.objects.filter(game=game_id)

    campaign_data = CampaignSerializer(campaigns, many=True).data
    factions_data = FactionPublicSerializer(factions, many=True).data
    fleets_data = FleetSerializer(fleets, many=True).data
    game_data = SimpleGameSerializer(game).data
    legions_data = LegionSerializer(legions, many=True).data
    logs_data = LogSerializer(logs, many=True).data
    senators_data = SenatorSerializer(senators, many=True).data
    wars_data = WarSerializer(wars, many=True).data

    timestamp = now().isoformat()

    player_ids = [f.player.id for f in factions]

    return (
        {
            "type": "public game state",
            "timestamp": timestamp,
            "game": game_data,
            "campaigns": campaign_data,
            "factions": factions_data,
            "fleets": fleets_data,
            "legions": legions_data,
            "logs": logs_data,
            "senators": senators_data,
            "wars": wars_data,
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
