from abc import ABC, abstractmethod
from typing import ClassVar, Dict, Optional

from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction


class ActionBase(ABC):
    NAME: ClassVar[str]

    @abstractmethod
    def validate(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        pass

    @abstractmethod
    def get_schema(
        self, game_state_snapshot: GameStateSnapshot, faction_id: int
    ) -> Optional[AvailableAction]:
        pass

    @abstractmethod
    def execute(self, game_id: int, faction_id: int, selection: Dict[str, str]) -> bool:
        pass
