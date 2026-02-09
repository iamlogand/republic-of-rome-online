from enum import Enum


class FactionStatusItem(Enum):
    AUCTION_WINNER = "auction winner"
    DONE = "done"
    CURRENT_BIDDER = "current bidder"
    CURRENT_INITIATIVE = "current initiative"
    SKIPPED = "skipped"
    CALLED_TO_VOTE = "called to vote"
    AWAITING_DECISION = "awaiting decision"

    @classmethod
    def bid(cls, n: int) -> str:
        """Generates a bid amount status."""
        return f"bid {n}T"

    @classmethod
    def initiative(cls, n: int) -> str:
        """Generates an initiative status."""
        return f"initiative {n}"
