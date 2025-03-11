from abc import ABC, abstractmethod

from rorapp.game_state.game_state_snapshot import GameStateSnapshot


class EffectBase(ABC):

    @abstractmethod
    def validate(self, game_state: GameStateSnapshot) -> bool:
        """To reduce DB load, this method's implementation should use the game state snapshot when possible."""
        pass

    @abstractmethod
    def execute(self, game_id: int) -> bool:
        pass
