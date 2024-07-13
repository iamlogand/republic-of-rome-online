import random


def draw_mortality_chits(chits_to_draw=1):
    """
    Draw mortality chits.

    Returns:
        list[int]: The list of drawn chit codes.
    """

    # Build a bag of chits
    lowest_code = 1
    highest_code = 30
    codes = list(range(lowest_code, highest_code + 1))
    chits = list(map(lambda code: str(code), codes))
    other_chits = ["none", "none", "none", "none", "draw 2", "draw 2"]
    chits = chits + other_chits
    random.shuffle(chits)

    # Draw chit(s)
    drawn_codes = []
    to_draw = chits_to_draw
    while to_draw > 0:
        to_draw -= 1

        # If there are no chits left, except the "Draw 2"s, then stop
        if len(chits) == 2:
            break

        # Draw the "Draw 2" chit
        chit_to_draw = chits[-1]
        if chit_to_draw == "draw 2":
            random.shuffle(chits)
            to_draw += 2
            continue

        # Draw any other chit
        drawn_chit = chits.pop()
        if drawn_chit != "none":
            drawn_codes.append(int(drawn_chit))

    return drawn_codes
