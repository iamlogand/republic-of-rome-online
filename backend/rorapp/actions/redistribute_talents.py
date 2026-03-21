from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator


class RedistributeTalentsAction(ActionBase):
    NAME = "Redistribute talents"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
        ):
            total_talents = (
                sum(
                    s.talents
                    for s in game_state.senators
                    if s.faction and s.faction.id == faction.id and s.alive
                )
                + faction.treasury
            )
            if total_talents > 0:
                return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            own_senators = sorted(
                [
                    s
                    for s in snapshot.senators
                    if s.faction and s.faction.id == faction.id and s.alive
                ],
                key=lambda s: s.name,
            )
            total = sum(s.talents for s in own_senators) + faction.treasury
            entries = [
                {"id": f"senator:{s.id}", "name": s.name, "current": s.talents}
                for s in own_senators
            ] + [
                {
                    "id": "faction_treasury",
                    "name": "Faction treasury",
                    "current": faction.treasury,
                }
            ]

            return [
                AvailableAction.objects.create(
                    game=snapshot.game,
                    faction=faction,
                    base_name=self.NAME,
                    position=self.POSITION,
                    schema=[
                        {
                            "type": "allocation",
                            "name": "Allocation",
                            "entries": entries,
                            "total": total,
                        }
                    ],
                )
            ]
        return []

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        allocation = selection.get("Allocation")
        if not isinstance(allocation, dict):
            return ExecutionResult(False)

        faction = Faction.objects.get(game=game_id, id=faction_id)
        own_senators = list(
            Senator.objects.filter(game=game_id, faction=faction_id, alive=True)
        )

        valid_ids = {f"senator:{s.id}" for s in own_senators} | {"faction_treasury"}
        original_total = sum(s.talents for s in own_senators) + faction.treasury

        # Validate keys
        if set(allocation.keys()) - valid_ids:
            return ExecutionResult(False)

        # Validate all values are non-negative integers
        try:
            values = {k: int(v) for k, v in allocation.items()}
        except (ValueError, TypeError):
            return ExecutionResult(False)

        if any(v < 0 for v in values.values()):
            return ExecutionResult(False)

        # Validate total matches
        if sum(values.values()) != original_total:
            return ExecutionResult(False)

        # Apply changes
        for senator in own_senators:
            key = f"senator:{senator.id}"
            senator.talents = values.get(key, 0)
            senator.save()

        faction.treasury = values.get("faction_treasury", faction.treasury)
        faction.save()

        return ExecutionResult(True)
