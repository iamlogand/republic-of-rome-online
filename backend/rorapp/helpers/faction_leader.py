from typing import Dict
from rorapp.models import Faction, Game, Log, Senator


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
            senator.save()

    # Assign faction leader title
    senator_id = int(selection["Faction leader"])
    faction_leader = senators.get(id=senator_id)
    if not faction_leader.has_title(Senator.Title.FACTION_LEADER):
        faction_leader.add_title(Senator.Title.FACTION_LEADER)
        faction_leader.save()

    # Logging
    game = Game.objects.get(id=game_id)
    faction = Faction.objects.get(id=faction_id)
    if previous_faction_leader:
        Log.create_object(
            game_id=game.id,
            text=f"{faction.display_name} selected {faction_leader.display_name} as their faction leader, replacing {previous_faction_leader.display_name}.",
        )
    else:
        Log.create_object(
            game_id=game.id,
            text=f"{faction.display_name} selected {faction_leader.display_name} as their faction leader.",
        )
