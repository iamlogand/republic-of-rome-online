from typing import List, Optional

from rorapp.models import AvailableAction, Faction, Game, Senator


class GameStateLive:
    def __init__(self, game_id: int):
        self.game_id = game_id

    @property
    def available_actions(self) -> List[AvailableAction]:
        return list(AvailableAction.objects.filter(game=self.game_id))

    @property
    def factions(self) -> List[Faction]:
        return list(Faction.objects.filter(game=self.game_id))

    @property
    def game(self) -> Game:
        return Game.objects.get(id=self.game_id)

    @property
    def senators(self) -> List[Senator]:
        return list(Senator.objects.filter(game=self.game_id))

    def get_available_action(self, available_action_id) -> Optional[AvailableAction]:
        return AvailableAction.objects.get(game=self.game_id, id=available_action_id)

    def get_faction(self, faction_id) -> Optional[Faction]:
        return Faction.objects.get(game=self.game_id, id=faction_id)

    def get_senator(self, senator_id) -> Optional[Senator]:
        return Senator.objects.get(game=self.game_id, id=senator_id)
