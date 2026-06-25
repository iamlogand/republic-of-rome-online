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
    POSITION = 200

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

        land_bill_targets = self._get_land_bill_targets(snapshot, faction)
        if land_bill_targets is not None:
            targetable_senators = land_bill_targets
        else:
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

        if not targetable_senators:
            return []

        assassin_card_count = sum(1 for c in faction.cards if c == "assassin")

        fields: list[dict] = [
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
                "group_by": "faction",
                "options": [
                    {"value": s.id, "object_class": "senator", "id": s.id}
                    for s in targetable_senators
                ],
            },
        ]

        if assassin_card_count > 0:
            fields.append(
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
                field_descriptors=fields,
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

        # §1.09.623: during a land bill with same-faction sponsors, only
        # sponsor/co-sponsor may be targeted.
        if self._is_land_bill_with_same_faction_sponsors(game):
            if not target.has_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL):
                return ExecutionResult(
                    False,
                    "During a land bill with same-faction sponsors, only the sponsor or co-sponsor may be targeted.",
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

        assassin_text = ""
        if assassin_cards_count > 0:
            assassin_text += f", playing {assassin_cards_count} assassin {'card' if assassin_cards_count == 1 else 'cards'}"
        Log.create_object(
            game_id,
            f"{attacker_faction.display_name} sent {assassin.display_name} to assassinate "
            f"{target.display_name}{assassin_text}.",
        )

        return ExecutionResult(True)

    def _is_land_bill_with_same_faction_sponsors(self, game: Game) -> bool:
        if (
            not game.current_proposal
            or "land bill" not in game.current_proposal.lower()
        ):
            return False
        sponsors = list(
            Senator.objects.filter(
                game=game,
                alive=True,
                status_items__contains=Senator.StatusItem.NAMED_IN_PROPOSAL.value,
            )
        )
        if len(sponsors) < 2:
            return False
        return all(s.faction_id == sponsors[0].faction_id for s in sponsors[1:])

    def _get_land_bill_targets(
        self, snapshot: GameStateSnapshot, faction: Faction
    ) -> Optional[List]:
        """
        If a land bill vote is in progress with same-faction sponsors,
        return only those sponsors as valid targets (§1.09.623).
        Returns None if the condition is not met (normal targeting applies).
        """
        game = snapshot.game
        if (
            not game.current_proposal
            or "land bill" not in game.current_proposal.lower()
        ):
            return None

        sponsors = sorted(
            [
                s
                for s in snapshot.senators
                if s.faction
                and s.has_status_item(Senator.StatusItem.NAMED_IN_PROPOSAL)
                and s.alive
                and s.location == "Rome"
            ],
            key=lambda s: s.family_name,
        )
        if len(sponsors) < 2:
            return None
        # All sponsors have a faction (guaranteed by the `s.faction` filter above)
        sponsor_faction = sponsors[0].faction
        if sponsor_faction is None:
            return None
        # Both sponsors must be from the same faction
        if not all(
            s.faction and s.faction.id == sponsor_faction.id for s in sponsors[1:]
        ):
            return None
        # Sponsors must be from a different faction than the attacker
        if sponsor_faction.id == faction.id:
            return None
        # Check if target faction was already targeted
        if sponsor_faction.has_status_item(FactionStatusItem.ASSASSINATION_TARGETED):
            return []
        return sponsors
