from abc import ABC, abstractmethod
from typing import ClassVar, Dict, Optional

from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction


class ActionBase(ABC):
    # Name is used for the button and the dialog title, if there is a dialog.
    NAME: ClassVar[str]

    # Generally, interesting actions are positioned on the left (lower number),
    # whilst boring actions are positioned on the right (higher number).
    POSITION: ClassVar[int] = 5

    @abstractmethod
    def validate(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        """To reduce DB load, this method's implementation should use the game state snapshot when possible."""
        pass

    @abstractmethod
    def get_schema(
        self, game_state_snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:
        """To reduce DB load, this method's implementation should use the game state snapshot when possible."""
        pass

    @abstractmethod
    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:
        pass
