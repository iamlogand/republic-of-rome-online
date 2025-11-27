from typing import List, Optional, Sequence, Tuple, Union
from abc import ABC, abstractmethod
import random

from rorapp.models.fleet import Fleet
from rorapp.models.legion import Legion


class RandomResolver(ABC):
    """
    Abstract base class for randomness resolution.
    """

    @abstractmethod
    def roll_dice(self, count: int = 1) -> int:
        """
        Roll 1d6 a given number of times.

        Returns:
            Total from dice rolls
        """
        pass

    @abstractmethod
    def select_casualties(
        self, units: Sequence[Union[Legion, Fleet]], count: int
    ) -> Tuple[List, List]:
        """
        Select which units are destroyed from a pool.

        Args:
            units: List or QuerySet of Fleet/Legion objects
            count: Number of units to destroy

        Returns:
            Tuple of (destroyed_units, surviving_units)
        """
        pass

    @abstractmethod
    def draw_mortality_chits(self, count: int = 1) -> List[str]:
        """
        Draw mortality chits for senator death checks.

        Args:
            count: Number of chits to draw

        Returns:
            List of chit codes
        """
        pass


class RealRandomResolver(RandomResolver):
    """
    Randomness resolver with genuinely random outcomes.
    """

    def roll_dice(self, count: int = 1) -> int:
        total = 0
        for _ in range(count):
            total += random.randint(1, 6)
        return total

    def select_casualties(
        self, units: Sequence[Union[Legion, Fleet]], losses: int
    ) -> Tuple[List, List]:
        units_list = list(units)
        random.shuffle(units_list)

        destroyed = units_list[:losses]
        survivors = units_list[losses:]

        destroyed.sort(key=lambda u: u.number)
        survivors.sort(key=lambda u: u.number)

        return destroyed, survivors

    def draw_mortality_chits(self, count: int = 1) -> List[str]:

        # Build a bag of chits
        lowest_code = 1
        highest_code = 30
        codes = list(range(lowest_code, highest_code + 1))
        numbered_chits = list(map(lambda code: str(code), codes))
        non_numbered_chits = ["none", "none", "none", "none", "draw 2", "draw 2"]
        chits = numbered_chits + non_numbered_chits
        random.shuffle(chits)

        # Draw chits
        drawn_codes = []
        to_draw = count
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
                drawn_codes.append(drawn_chit)

        return drawn_codes


class FakeRandomResolver(RandomResolver):
    """
    Randomness resolver with controllable outcomes.
    """

    def __init__(self) -> None:
        self.dice_roll_index = 0
        self.dice_rolls: Optional[List[int]] = None
        self.casualty_order: Optional[List[str]] = None
        self.mortality_chits: Optional[List[str]] = None

    def roll_dice(self, count: int = 1) -> int:
        if self.dice_rolls is None or len(self.dice_rolls) < 1:
            raise ValueError("Dice roll not set in FakeRandomResolver.")
        roll = self.dice_rolls[self.dice_roll_index]
        if self.dice_roll_index + 1 < len(self.dice_rolls):
            self.dice_roll_index += 1
        else:
            self.dice_roll_index = 0
        return roll

    def select_casualties(
        self, units: Sequence[Union[Legion, Fleet]], losses: int
    ) -> Tuple[List, List]:
        units_list = list(units)

        casualty_order = self.casualty_order
        if casualty_order is None:
            raise ValueError("Casualty order not set in FakeRandomResolver.")

        def sort_key(unit: Union[Legion, Fleet]) -> int:
            try:
                return casualty_order.index(unit.name)
            except ValueError:
                # If unit not in override list, put it at the end
                return len(casualty_order) + unit.number

        units_list.sort(key=sort_key)

        destroyed = units_list[:losses]
        survivors = units_list[losses:]

        destroyed.sort(key=lambda u: u.number)
        survivors.sort(key=lambda u: u.number)

        return destroyed, survivors

    def draw_mortality_chits(self, count: int = 1) -> List[str]:
        if self.mortality_chits is None:
            raise ValueError("Mortality chits not set in FakeRandomResolver.")
        return self.mortality_chits[:count]

    def reset(self) -> None:
        self.dice_roll = None
        self.casualty_order = None
        self.mortality_chits = None
