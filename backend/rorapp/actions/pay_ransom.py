from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.hrao import set_hrao
from rorapp.models import AvailableAction, Faction, Log, Senator


def ransomable_captives(
    game_state: GameStateLive | GameStateSnapshot, faction: Faction
) -> List[Senator]:
    """Captives whose own and faction treasuries can pay the ransom (1.10.71)."""

    return sorted(
        (
            s
            for s in game_state.senators
            if s.faction_id == faction.id
            and s.alive
            and s.captive
            and s.talents + faction.treasury >= s.ransom
        ),
        key=lambda s: s.family_name,
    )


class PayRansomAction(ActionBase):
    NAME = "Pay ransom"
    POSITION = 3

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction or not ransomable_captives(game_state, faction):
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {
                        "type": "select",
                        "name": "Captive",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                                "signals": {
                                    "ransom": s.ransom,
                                    "min_from_treasury": max(0, s.ransom - s.talents),
                                    "max_from_treasury": min(
                                        faction.treasury, s.ransom
                                    ),
                                },
                            }
                            for s in ransomable_captives(snapshot, faction)
                        ],
                    },
                    {
                        "type": "calculation",
                        "name": "Ransom",
                        "value": "signal:ransom",
                        "conditions": [
                            {"value1": "signal:ransom", "operation": ">", "value2": 0}
                        ],
                    },
                    {
                        "type": "number",
                        "name": "Talents from the faction treasury",
                        "min": ["signal:min_from_treasury"],
                        "max": ["signal:max_from_treasury"],
                    },
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
        faction = Faction.objects.get(game=game_id, id=faction_id)
        captive = Senator.objects.filter(
            game=game_id,
            faction=faction_id,
            alive=True,
            captor__isnull=False,
            id=selection["Captive"],
        ).first()
        if not captive:
            return ExecutionResult(False, "Invalid captive selected.")

        # Ransom money comes from the captive's own and faction treasuries (1.10.71)
        ransom = captive.ransom
        from_treasury = int(selection.get("Talents from the faction treasury", 0))
        if from_treasury < 0 or from_treasury > min(faction.treasury, ransom):
            return ExecutionResult(False, "The faction treasury cannot pay that much.")
        if ransom - from_treasury > captive.talents:
            return ExecutionResult(
                False, f"{captive.display_name} cannot cover the rest of the ransom."
            )

        faction.treasury -= from_treasury
        faction.save()
        captive.talents -= ransom - from_treasury
        captive.captor = None
        # Captives return to Rome when ransomed (1.10.71)
        captive.location = "Rome"
        captive.save()

        Log.create_object(
            game_id, f"{captive.display_name} was ransomed for {ransom}T and returned to Rome."
        )
        set_hrao(game_id)
        return ExecutionResult(True)
