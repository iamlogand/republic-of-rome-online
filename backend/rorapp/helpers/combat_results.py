DEFEAT = "defeat"
DISASTER = "disaster"
STALEMATE = "stalemate"
STANDOFF = "standoff"
VICTORY = "victory"


def combat_result(modified_result: int) -> str:
    """The Combat Results Table row for a modified 3d6 roll (1.10.11)."""

    if modified_result < 8:
        return DEFEAT
    if modified_result < 14:
        return STALEMATE
    return VICTORY


def combat_losses(result: str, modified_result: int, unit_count: int) -> int:
    """Units a force of `unit_count` loses on the Combat Results Table (1.10.11)."""

    if result == DISASTER:
        return (unit_count + 1) // 2
    if result == STANDOFF:
        return (unit_count + 3) // 4
    if result == DEFEAT:
        if modified_result < 4:
            return unit_count
        return min(8 - modified_result, unit_count)
    if result == STALEMATE:
        return min(13 - modified_result, unit_count)
    if modified_result < 18:
        return min(18 - modified_result, unit_count)
    return 0
