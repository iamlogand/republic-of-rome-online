from typing import Optional
from rorapp.models import Faction


def get_next_faction_in_forum_phase(
    last_faction: Faction | None = None
) -> Optional[Faction]:
    """
    Find the faction that should take the next initiative in the forum phase.

    Args:
        last_faction (Faction): The faction that took the last initiative.

    Returns:
        Faction | None: The faction that should take the next initiative, if there is one.
    """

    factions = Faction.objects.filter(game__id=last_faction.game.id).order_by("rank")
    if last_faction is None:
        return factions.first()
    last_faction_index = list(factions).index(last_faction)
    next_faction_index = last_faction_index + 1
    if next_faction_index >= len(factions):
        return None
    return factions[next_faction_index]
