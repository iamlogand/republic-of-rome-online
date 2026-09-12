from rorapp.models import Senator


def persuasion_modifier(
    persuader: Senator, target: Senator, bribe: int, evil_omens: int
) -> int:
    """Return the modified base number for a persuasion attempt (1.07.41)."""
    return (
        persuader.oratory
        + persuader.influence
        + bribe
        + evil_omens
        - target.loyalty
        - target.talents
        - (7 if target.faction_id else 0)
    )
