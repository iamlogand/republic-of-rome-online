def persuasion_success_chance(modified_base: int, threshold: int) -> int:
    """Return the 2d6 success chance as a rounded percentage."""
    successes = sum(
        1
        for d1 in range(1, 7)
        for d2 in range(1, 7)
        if d1 + d2 <= modified_base and d1 + d2 < threshold
    )
    return round(successes / 36 * 100)
