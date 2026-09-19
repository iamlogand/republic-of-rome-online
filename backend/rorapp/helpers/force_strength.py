def force_strength(force: int, military: int) -> int:
    """Strength of a force, with the commander's Military rating capped by it (1.10.11)."""

    return force + min(military, force)
