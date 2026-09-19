from typing import Sequence

from rorapp.classes.random_resolver import RandomResolver


def shuffle_card_into_top(
    deck: Sequence[str],
    card: str,
    count: int,
    random_resolver: RandomResolver,
) -> list[str]:
    top_count = min(count, len(deck))
    top_cards = list(deck[:top_count]) + [card]
    remaining_cards = list(deck[top_count:])
    return random_resolver.shuffle_cards(top_cards) + remaining_cards
