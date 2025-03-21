from typing import List, Optional

from rorapp.models import AvailableAction, Faction, Game, Senator, War


class GameStateSnapshot:
    def __init__(self, game_id: int):
        self.available_actions: List[AvailableAction] = list(
            AvailableAction.objects.filter(game=game_id)
        )
        self.factions: List[Faction] = list(Faction.objects.filter(game=game_id))
        self.game: Game = Game.objects.get(id=game_id)
        self.senators: List[Senator] = list(Senator.objects.filter(game=game_id))
        self.wars: List[War] = list(War.objects.filter(game=game_id))

    def get_available_action(self, available_action_id) -> Optional[AvailableAction]:
        return next(
            (f for f in self.available_actions if f.id == available_action_id), None
        )

    def get_faction(self, faction_id) -> Optional[Faction]:
        return next((f for f in self.factions if f.id == faction_id), None)

    def get_senator(self, senator_id) -> Optional[Senator]:
        return next((f for f in self.senators if f.id == senator_id), None)
