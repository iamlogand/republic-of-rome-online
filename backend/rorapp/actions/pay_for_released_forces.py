from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.rebel_maintenance import MAINTENANCE_COST, released_legions
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Faction, Game, Legion, Log, Senator


def hrao_faction(
    game_state: GameStateLive | GameStateSnapshot, faction_id: int
) -> Optional[Faction]:
    """The HRAO's faction, which decides the fate of released forces (1.11.35)."""

    faction = game_state.get_faction(faction_id)
    if not faction or not (
        game_state.game.phase == Game.Phase.REVENUE
        and game_state.game.sub_phase == Game.SubPhase.REBEL_MAINTENANCE
    ):
        return None
    if not released_legions(faction.game_id):
        return None
    hrao = next(
        (s for s in game_state.senators if s.has_title(Senator.Title.HRAO)), None
    )
    if not hrao or hrao.faction_id != faction.id:
        return None
    return faction


class PayForReleasedForcesAction(ActionBase):
    NAME = "Pay for released forces"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = hrao_faction(game_state, faction_id)
        if not faction:
            return None
        cost = MAINTENANCE_COST * len(released_legions(faction.game_id))
        if game_state.game.state_treasury < cost:
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []
        legions = released_legions(snapshot.game.id)
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[],
                context={"cost": MAINTENANCE_COST * len(legions)},
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        legions = released_legions(game_id)
        if not legions:
            return ExecutionResult(False, "There are no released forces.")

        game = Game.objects.get(id=game_id)
        cost = MAINTENANCE_COST * len(legions)
        if game.state_treasury < cost:
            return ExecutionResult(
                False, "The State treasury cannot afford these forces."
            )

        game.state_treasury -= cost
        game.save()
        for legion in legions:
            legion.released = False
        Legion.objects.bulk_update(legions, ["released"])
        Log.create_object(
            game_id,
            f"The State paid {cost}T to take on "
            f"{unit_list_to_string(legions, [])} released by the rebels.",
        )
        return ExecutionResult(True)
