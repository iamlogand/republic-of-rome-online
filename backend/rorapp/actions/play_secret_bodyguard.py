from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class PlaySecretBodyguardAction(ActionBase):
    NAME = "Play secret bodyguard"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if game_state.game.phase != Game.Phase.SENATE:
            return None
        if game_state.game.sub_phase != Game.SubPhase.ASSASSINATION_RESOLUTION:
            return None
        if not faction.has_status_item(FactionStatusItem.AWAITING_DECISION):
            return None
        # Must be the target faction
        has_target = any(
            s
            for s in game_state.senators
            if s.faction
            and s.faction.id == faction.id
            and s.has_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
        )
        if not has_target:
            return None
        # Must actually hold at least one secret bodyguard card
        bodyguard_count = sum(1 for c in faction.cards if c == "secret bodyguard")
        if bodyguard_count == 0:
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        bodyguard_count = sum(1 for c in faction.cards if c == "secret bodyguard")

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "number",
                        "name": "Secret bodyguards to play",
                        "min": [1],
                        "max": [bodyguard_count],
                    }
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
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)
        count = int(selection["Secret bodyguards to play"])

        available = sum(1 for c in faction.cards if c == "secret bodyguard")
        if count < 1 or count > available:
            return ExecutionResult(False, "Invalid number of Secret Bodyguard cards.")

        senators = list(Senator.objects.filter(game=game_id, alive=True))
        assassin = next(
            (s for s in senators if s.has_status_item(Senator.StatusItem.ASSASSIN)),
            None,
        )
        if assassin is None:
            return ExecutionResult(False, "No assassin found.")

        # Discard the played cards
        remaining_cards = list(faction.cards)
        for _ in range(count):
            remaining_cards.remove("secret bodyguard")
        faction.cards = remaining_cards
        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()

        # Apply subtraction to the roll result
        game.assassination_roll_result -= count

        if game.assassination_roll_result <= 2:
            # Subtraction alone caught the assassin — no rerolls needed
            assassin.add_status_item(Senator.StatusItem.CAUGHT)
            assassin.save()
            game.bodyguard_rerolls_remaining = 0
        else:
            # Schedule catch rerolls (one per bodyguard card played)
            game.bodyguard_rerolls_remaining = count

        game.save()

        cards_text = f"{count} Secret Bodyguard card{'s' if count > 1 else ''}"
        Log.create_object(
            game_id,
            f"{faction.display_name} played {cards_text}. "
            f"Roll result reduced to {game.assassination_roll_result}.",
        )

        return ExecutionResult(True)
