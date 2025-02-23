from typing import Dict
from rorapp.models import Game, Log, Senator


def assign_faction_leader(
    game_id: int, faction_id: int, selection: Dict[str, str]
) -> None:

    # Remove faction leader titles
    senators = Senator.objects.filter(game_id=game_id, faction=faction_id, alive=True)
    previous_faction_leader = None
    for senator in senators:
        if senator.has_title(Senator.Title.FACTION_LEADER):
            previous_faction_leader = senator
            senator.remove_title(Senator.Title.FACTION_LEADER)

    # Assign faction leader title
    senator_id = int(selection["Faction leader"])
    faction_leader = senators.get(id=senator_id)
    if not faction_leader.has_title(Senator.Title.FACTION_LEADER):
        faction_leader.add_title(Senator.Title.FACTION_LEADER)
        faction_leader.save()

    # Logging
    game = Game.objects.get(id=game_id)
    if previous_faction_leader:
        Log.objects.create(
            game=game,
            text=f"{faction_leader.display_name} has replaced {previous_faction_leader.display_name} as faction leader.",
        )
    else:
        Log.objects.create(
            game=game,
            text=f"{faction_leader.display_name} has become faction leader.",
        )
