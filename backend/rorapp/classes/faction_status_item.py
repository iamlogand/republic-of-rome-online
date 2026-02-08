from enum import Enum


class FactionStatusItem(Enum):
    AUCTION_WINNER = "Auction winner"
    DONE = "Done"
    CURRENT_BIDDER = "Current bidder"
    CURRENT_INITIATIVE = "Current initiative"
    SKIPPED = "Skipped"
    CALLED_TO_VOTE = "Called to vote"
    ACTION_PENDING = "Action pending"

    @classmethod
    def bid(cls, n: int) -> str:
        """Generates a bid amount status."""
        return f"Bid {n}T"

    @classmethod
    def initiative(cls, n: int) -> str:
        """Generates an initiative status."""
        return f"Initiative {n}"
