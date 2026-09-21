from typing import List

from rorapp.models import Faction, Senator


def faction_senators_attending_senate(game_id: int, faction: Faction) -> List[Senator]:
    # Only senators in Rome attend the meeting and control votes (1.09.11, 1.09.13)
    return list(
        Senator.objects.filter(
            game_id=game_id, faction=faction, alive=True, location="Rome"
        )
    )
