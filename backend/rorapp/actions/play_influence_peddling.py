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
    POSITION = 201

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

        target_options = [
            {"value": f"faction:{f.id}", "name": f.display_name}
            for f in snapshot.factions
            if f.id != faction_id and f.cards
        ]
        if not target_options:
            return []

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {"type": "select", "name": "Target", "options": target_options},
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
        target_value = selection.get("Target")
        if not target_value or not str(target_value).startswith("faction:"):
            return ExecutionResult(False, "Invalid target.")
        try:
            target_id = int(str(target_value)[len("faction:") :])
        except ValueError:
            return ExecutionResult(False, "Invalid target.")

        if target_id == faction_id:
            return ExecutionResult(False, "Cannot target your own faction.")

        faction = Faction.objects.get(game=game_id, id=faction_id)
        if not faction.has_card("influence peddling"):
            return ExecutionResult(False, "No Influence Peddling card in hand.")

        target = Faction.objects.filter(game=game_id, id=target_id).first()
        if not target:
            return ExecutionResult(False, "Target not found.")
        if not target.cards:
            return ExecutionResult(False, "Target has no cards.")

        drawn_card = random.choice(target.cards)

        faction.remove_card("influence peddling")
        faction.add_card(drawn_card)
        faction.save()

        target.remove_card(drawn_card)
        target.save()

        Log.create_object(
            game_id,
            f"{faction.display_name} played Influence Peddling, stealing a random card from {target.display_name}.",
        )

        return ExecutionResult(True)
