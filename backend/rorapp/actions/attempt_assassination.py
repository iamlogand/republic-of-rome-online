from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


_EXCLUDED_SUB_PHASES = {
    Game.SubPhase.START,
    Game.SubPhase.END,
    Game.SubPhase.ASSASSINATION_RESOLUTION,
}


class AttemptAssassinationAction(ActionBase):
    NAME = "Attempt assassination"
    POSITION = 9

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if game_state.game.phase != Game.Phase.SENATE:
            return None
        if game_state.game.sub_phase in _EXCLUDED_SUB_PHASES:
            return None
        if faction.has_status_item(FactionStatusItem.ATTEMPTED_ASSASSINATION):
            return None
        # Faction must have at least one alive senator in Rome
        has_senator_in_rome = any(
            s
            for s in game_state.senators
            if s.faction
            and s.faction.id == faction.id
            and s.alive
            and s.location == "Rome"
        )
        if not has_senator_in_rome:
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        own_senators = sorted(
            [
                s
                for s in snapshot.senators
                if s.faction
                and s.faction.id == faction.id
                and s.alive
                and s.location == "Rome"
            ],
            key=lambda s: s.family_name,
        )

        targetable_senators = sorted(
            [
                s
                for s in snapshot.senators
                if s.faction
                and s.faction.id != faction.id
                and s.alive
                and s.location == "Rome"
                and not s.faction.has_status_item(
                    FactionStatusItem.ASSASSINATION_TARGETED
                )
            ],
            key=lambda s: s.family_name,
        )

        assassin_card_count = sum(1 for c in faction.cards if c == "assassin")

        schema: list[dict] = [
            {
                "type": "select",
                "name": "Assassin",
                "options": [
                    {"value": s.id, "object_class": "senator", "id": s.id}
                    for s in own_senators
                ],
            },
            {
                "type": "select",
                "name": "Target",
                "options": [
                    {"value": s.id, "object_class": "senator", "id": s.id}
                    for s in targetable_senators
                ],
            },
        ]

        if assassin_card_count > 0:
            schema.append(
                {
                    "type": "number",
                    "name": "Assassin cards",
                    "min": [0],
                    "max": [assassin_card_count],
                }
            )

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=schema,
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
        attacker_faction = Faction.objects.get(game=game_id, id=faction_id)

        assassin_id = selection["Assassin"]
        target_id = selection["Target"]
        assassin_cards_count = int(selection.get("Assassin cards", 0))

        assassin = Senator.objects.get(game=game_id, id=assassin_id)
        target = Senator.objects.get(game=game_id, id=target_id)

        if not assassin.alive or assassin.location != "Rome":
            return ExecutionResult(False, "Assassin is not available.")
        if not target.alive or target.location != "Rome":
            return ExecutionResult(False, "Target is not available.")
        if assassin.faction_id != faction_id:
            return ExecutionResult(False, "Assassin must belong to your faction.")
        if target.faction_id == faction_id:
            return ExecutionResult(
                False, "Cannot assassinate a member of your own faction."
            )

        assert target.faction_id is not None
        target_faction = Faction.objects.get(game=game_id, id=target.faction_id)
        if target_faction.has_status_item(FactionStatusItem.ASSASSINATION_TARGETED):
            return ExecutionResult(
                False, "That faction has already been targeted this turn."
            )

        available_assassin_cards = sum(
            1 for c in attacker_faction.cards if c == "assassin"
        )
        if assassin_cards_count > available_assassin_cards:
            return ExecutionResult(False, "Not enough Assassin cards.")

        # Remove played Assassin cards from hand
        remaining_cards = list(attacker_faction.cards)
        for _ in range(assassin_cards_count):
            remaining_cards.remove("assassin")
        attacker_faction.cards = remaining_cards
        attacker_faction.add_status_item(FactionStatusItem.ATTEMPTED_ASSASSINATION)
        attacker_faction.save()

        target_faction.add_status_item(FactionStatusItem.ASSASSINATION_TARGETED)
        target_faction.save()

        game.assassination_roll_modifier = assassin_cards_count
        game.interrupted_sub_phase = game.sub_phase or ""
        game.sub_phase = Game.SubPhase.ASSASSINATION_RESOLUTION
        game.save()

        assassin.add_status_item(Senator.StatusItem.ASSASSIN)
        assassin.save()
        target.add_status_item(Senator.StatusItem.ASSASSINATION_TARGET)
        target.save()

        modifier_text = (
            f" (+{assassin_cards_count})" if assassin_cards_count > 0 else ""
        )
        Log.create_object(
            game_id,
            f"{attacker_faction.display_name} sent {assassin.display_name} to assassinate "
            f"{target.display_name}{modifier_text}.",
        )

        return ExecutionResult(True)
