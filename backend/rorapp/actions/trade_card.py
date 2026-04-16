from typing import Any, Dict, List, Optional
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.concession import Concession
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.game_data import load_statesmen
from rorapp.models import AvailableAction, Faction, Game, Log


def _card_display_name(card: str) -> str:
    if card.startswith("statesman:"):
        code = card[len("statesman:"):]
        statesmen = load_statesmen()
        return next(
            (k for k, v in statesmen.items() if v["code"] == code), card
        )
    if card.startswith("concession:"):
        value = card[len("concession:"):]
        concession = next((c for c in Concession if c.value == value), None)
        return concession.value.title() if concession else value
    return card


class TradeCardAction(ActionBase):
    NAME = "Trade card"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.CARD_TRADING
            and not faction.has_status_item(FactionStatusItem.DONE)
            and faction.cards
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        card_options = [
            {"value": card, "name": _card_display_name(card)}
            for card in faction.cards
        ]
        recipient_options = [
            {"value": f"faction:{f.id}", "name": f.display_name}
            for f in snapshot.factions
            if f.id != faction_id
        ]

        if not recipient_options:
            return []

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {"type": "select", "name": "Card", "options": card_options},
                    {"type": "select", "name": "Recipient", "options": recipient_options},
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
        card = selection.get("Card")
        recipient_value = selection.get("Recipient")
        if not card or not recipient_value:
            return ExecutionResult(False)

        faction = Faction.objects.get(game=game_id, id=faction_id)
        if not faction.has_card(card):
            return ExecutionResult(False)

        if not str(recipient_value).startswith("faction:"):
            return ExecutionResult(False)
        try:
            recipient_id = int(str(recipient_value)[len("faction:"):])
        except ValueError:
            return ExecutionResult(False)

        if recipient_id == faction_id:
            return ExecutionResult(False)

        recipient = Faction.objects.filter(game=game_id, id=recipient_id).first()
        if not recipient:
            return ExecutionResult(False)

        faction.remove_card(card)
        faction.save()
        recipient.add_card(card)
        recipient.remove_status_item(FactionStatusItem.DONE)
        recipient.save()

        Log.create_object(
            game_id=game_id,
            text=f"{faction.display_name} gave a card to {recipient.display_name}.",
        )

        return ExecutionResult(True)
