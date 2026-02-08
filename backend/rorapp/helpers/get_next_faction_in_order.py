from rorapp.models import Faction


def get_next_faction_in_order(factions, current_position: int) -> Faction:
    """Get the next faction in position order, wrapping around."""

    positions = [f.position for f in factions.order_by("position")]
    next_position_index = positions.index(current_position) + 1
    next_position = (
        positions[next_position_index]
        if next_position_index < len(positions)
        else positions[0]
    )
    return factions.get(position=next_position)
