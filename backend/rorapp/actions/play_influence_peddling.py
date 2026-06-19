import random
from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log


class PlayInfluencePeddlingAction(ActionBase):
    NAME = "Play influence peddling"
    POSITION = 200

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            not faction
            or not faction.has_card("influence peddling")
            or game_state.game.phase == Game.Phase.REVOLUTION
            or not any(f for f in game_state.factions if f.id != faction_id and f.cards)
        ):
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        opponent_options = [
            {"value": f"faction:{f.id}", "name": f.display_name}
            for f in snapshot.factions
            if f.id != faction_id and f.cards
        ]
        if not opponent_options:
            return []

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {"type": "select", "name": "Opponent", "options": opponent_options},
                ],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        opponent_value = selection.get("Opponent")
        if not opponent_value or not str(opponent_value).startswith("faction:"):
            return ExecutionResult(False, "Invalid opponent.")
        try:
            opponent_id = int(str(opponent_value)[len("faction:") :])
        except ValueError:
            return ExecutionResult(False, "Invalid opponent.")

        if opponent_id == faction_id:
            return ExecutionResult(False, "Cannot target your own faction.")

        faction = Faction.objects.get(game=game_id, id=faction_id)
        if not faction.has_card("influence peddling"):
            return ExecutionResult(False, "No Influence Peddling card in hand.")

        opponent = Faction.objects.filter(game=game_id, id=opponent_id).first()
        if not opponent:
            return ExecutionResult(False, "Opponent not found.")
        if not opponent.cards:
            return ExecutionResult(False, "Opponent has no cards.")

        drawn_card = random.choice(opponent.cards)

        faction.remove_card("influence peddling")
        faction.add_card(drawn_card)
        faction.save()

        opponent.remove_card(drawn_card)
        opponent.save()

        Log.create_object(
            game_id,
            f"{faction.display_name} played Influence Peddling, stealing a random card from {opponent.display_name}.",
        )

        return ExecutionResult(True)
