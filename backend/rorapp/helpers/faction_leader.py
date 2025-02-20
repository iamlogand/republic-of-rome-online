from typing import Dict
from rorapp.models import Senator


def assign_faction_leader(
    game_id: int, faction_id: int, selection: Dict[str, str]
) -> None:

    # Remove faction leader titles
    senators = Senator.objects.filter(game_id=game_id, faction=faction_id, alive=True)
    for senator in senators:
        senator.remove_title(Senator.Title.FACTION_LEADER)

    # Assign faction leader title
    senator_id = int(selection["Faction leader"])
    senator = senators.get(id=senator_id)
    if not senator.has_title(Senator.Title.FACTION_LEADER):
        senator.add_title(Senator.Title.FACTION_LEADER)
        senator.save()
