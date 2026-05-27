from typing import Any, Dict, Optional, List

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.text import pluralize
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class PressureKnightAction(ActionBase):
    NAME = "Pressure knight"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        if (
            game_state.game.phase != Game.Phase.FORUM
            or game_state.game.sub_phase != Game.SubPhase.ATTRACT_KNIGHT
            or not faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE)
        ):
            return None

        # Must control at least one knight to offer the action
        total_knights = sum(
            s.knights
            for s in game_state.senators
            if s.faction and s.faction.id == faction.id and s.alive
        )
        if total_knights == 0:
            return None

        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        eligible_senators = sorted(
            [
                s
                for s in snapshot.senators
                if s.faction
                and s.faction.id == faction.id
                and s.alive
                and s.knights > 0
            ],
            key=lambda s: (s.family_name, s.generation),
        )

        entries = [
            {
                "senator_id": s.id,
                "name": s.display_name,
                "max": s.knights,
            }
            for s in eligible_senators
        ]

        schema: List[dict] = []
        if entries:
            schema.append(
                {
                    "type": "per_senator_number",
                    "name": "Pressures",
                    "entries": entries,
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

        pressures_raw = (
            selection.get("Pressures")
            or selection.get("pressures")
            or selection.get("senator_pressures")
            or selection.get("PressuredKnights")
        )
        if not isinstance(pressures_raw, dict):
            return ExecutionResult(False, "Invalid pressure selection data.")

        # Normalize to {senator_id: count}
        pressures: Dict[int, int] = {}
        for key, count in pressures_raw.items():
            try:
                if isinstance(key, str) and key.startswith("senator:"):
                    sid = int(key.split(":", 1)[1])
                else:
                    sid = int(key)
                num = int(count)
            except (ValueError, TypeError):
                return ExecutionResult(False, "Invalid senator id or knight count.")

            if num < 0:
                return ExecutionResult(False, "Cannot pressure a negative number of knights.")
            if num > 0:
                pressures[sid] = pressures.get(sid, 0) + num

        if not pressures:
            # Player chose to pressure zero knights total — treat as a no-op (advance phase)
            self.save_game(game_id)
            return ExecutionResult(True)

        senators = list(
            Senator.objects.filter(game=game_id, faction=faction_id, alive=True)
        )
        senator_by_id = {s.id: s for s in senators}

        # Validate all targets and counts
        for sid, num in pressures.items():
            senator = senator_by_id.get(sid)
            if not senator:
                return ExecutionResult(False, f"Senator {sid} is not in your faction.")
            if num > senator.knights:
                return ExecutionResult(False, f"{senator.display_name} does not have {num} knights.")

        # Perform the pressure: one die roll per pressured knight
        rolls_by_senator: Dict[int, List[int]] = {}

        for sid, num in pressures.items():
            senator = senator_by_id[sid]
            rolls = [random_resolver.roll_dice() for _ in range(num)]
            rolls_by_senator[sid] = rolls
            senator.talents += sum(rolls)
            senator.knights -= num

        # Persist senator changes
        Senator.objects.bulk_update(
            [s for s in senators if s.id in rolls_by_senator],
            ["talents", "knights"],
        )

        # Logging
        log_parts = []
        for sid, rolls in rolls_by_senator.items():
            senator = senator_by_id[sid]
            gain = sum(rolls)
            n = len(rolls)
            roll_str = ", ".join(str(r) for r in rolls)
            log_parts.append(
                f"{senator.display_name} pressured {pluralize(n, 'knight')} for {gain}T ({roll_str})"
            )

        if log_parts:
            Log.create_object(
                game_id=game_id,
                text="; ".join(log_parts) + ".",
            )

        # Progress game
        self.save_game(game_id)

        return ExecutionResult(True)

    def _save_game(self, game_id):
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.SPONSOR_GAMES
        game.save()
