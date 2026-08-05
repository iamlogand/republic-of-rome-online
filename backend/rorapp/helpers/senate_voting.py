from typing import List

from rorapp.models import Faction, Senator


def faction_senators_attending_senate(game_id: int, faction: Faction) -> List[Senator]:
    return list(
        Senator.objects.filter(
            game_id=game_id, faction=faction, alive=True, location="Rome"
        )
    )
