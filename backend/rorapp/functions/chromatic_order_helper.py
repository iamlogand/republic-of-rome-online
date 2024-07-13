from rorapp.models import Faction


def get_next_faction_in_chromatic_order(
    last_faction: Faction,
) -> Faction | None:
    """
    Find the faction that should take the next action or set of actions when rotating through players in Chromatic order.

    Args:
        last_faction (Faction): The faction that took the last actions.

    Returns:
        Faction | None: The faction that should take actions, if there is one.
    """

    factions = Faction.objects.filter(game__id=last_faction.game.id).order_by("rank")
    last_faction_index = list(factions).index(last_faction)
    next_faction_index = last_faction_index + 1
    if next_faction_index >= len(factions):
        return None
    return factions[next_faction_index]
