from rorapp.classes.random_resolver import FakeRandomResolver
from rorapp.helpers.deck import shuffle_card_into_top


def test_shuffle_card_into_top_only_reorders_requested_top_cards():
    # Arrange
    deck = ["A", "B", "C", "D", "E", "F", "G", "H"]
    resolver = FakeRandomResolver()
    resolver.card_shuffle_results = [["C", "X", "A", "F", "B", "E", "D"]]

    # Act
    shuffled_deck = shuffle_card_into_top(deck, "X", 6, resolver)

    # Assert
    assert shuffled_deck == ["C", "X", "A", "F", "B", "E", "D", "G", "H"]
    assert deck == ["A", "B", "C", "D", "E", "F", "G", "H"]


def test_shuffle_card_into_top_uses_all_cards_when_fewer_than_count_remain():
    # Arrange
    deck = ["A", "B", "C"]
    resolver = FakeRandomResolver()
    resolver.card_shuffle_results = [["X", "C", "A", "B"]]

    # Act
    shuffled_deck = shuffle_card_into_top(deck, "X", 6, resolver)

    # Assert
    assert shuffled_deck == ["X", "C", "A", "B"]


def test_shuffle_card_into_top_handles_empty_deck():
    # Arrange
    resolver = FakeRandomResolver()

    # Act
    shuffled_deck = shuffle_card_into_top([], "X", 6, resolver)

    # Assert
    assert shuffled_deck == ["X"]
