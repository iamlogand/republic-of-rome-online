from typing import Union


ACCUSED_KILLED = "killed"
ACCUSED_FREED = "freed"


def popular_appeal_outcome(result: int) -> Union[str, int]:
    """
    Popular Appeal Table (1.09.421).

    Returns "killed", "freed", or the number of votes gained. A negative number
    is votes for conviction, a positive number is votes against conviction.
    """
    if result <= 0:
        return ACCUSED_KILLED
    if result >= 12:
        return ACCUSED_FREED
    return {1: -9, 2: -7, 3: -5, 4: -3, 5: -1, 6: 0, 7: 1, 8: 3, 9: 5, 10: 7, 11: 9}[
        result
    ]
