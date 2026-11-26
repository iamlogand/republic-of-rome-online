from typing import Optional

from rorapp.helpers.enemy_leaders import get_matching_enemy_leaders
from rorapp.helpers.force_strength import force_strength
from rorapp.models import War


def get_minimum_force_error(
    war: War, land_force: int, naval_force: int
) -> Optional[str]:
    if war.naval_strength == 0:
        if land_force == 0:
            return "A minimum of 1 legion is required for the land battle."
        if not war.has_required_fleets(naval_force):
            fleets_text = (
                str(war.fleet_support)
                + " fleet"
                + ("s are" if war.fleet_support > 1 else " is")
            )
            return f"Insufficient fleet support: at least {fleets_text} required to support the land battle."
    else:
        if naval_force == 0:
            return "A minimum of 1 fleet is required for the naval battle."
    return None


def requires_force_consent(
    game_id: int, war: War, land_force: int, naval_force: int, military: int
) -> bool:
    leader_strength = sum(
        l.strength for l in get_matching_enemy_leaders(game_id, war, active=True)
    )
    if war.naval_strength > 0:
        return force_strength(naval_force, military) < war.naval_strength + leader_strength
    return force_strength(land_force, military) < war.land_strength + leader_strength
