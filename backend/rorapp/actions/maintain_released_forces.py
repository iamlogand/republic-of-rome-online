from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Faction, Fleet, Game, Legion, Log, Senator


class MaintainReleasedForcesAction(ActionBase):
    NAME = "Maintain released forces"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if not (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.RELEASED_FORCES_MAINTENANCE
            and faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
        ):
            return None
        hrao = next(
            (s for s in game_state.senators if s.has_title(Senator.Title.HRAO)),
            None,
        )
        if not hrao or hrao.faction_id != faction_id:
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        released_legions = sorted(
            [l for l in snapshot.legions if l.released_by_rebel],
            key=lambda l: l.number,
        )
        released_fleets = sorted(
            [f for f in snapshot.fleets if f.released_by_rebel],
            key=lambda f: f.number,
        )

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {
                        "type": "multiselect",
                        "name": "Legions",
                        "options": [
                            {"value": l.id, "object_class": "legion", "id": l.id}
                            for l in released_legions
                        ],
                    },
                    {
                        "type": "multiselect",
                        "name": "Fleets",
                        "options": [
                            {"value": f.id, "object_class": "fleet", "id": f.id}
                            for f in released_fleets
                        ],
                        "inline": True,
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
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, id=faction_id)

        legion_ids = [int(i) for i in selection.get("Legions", [])]
        fleet_ids = [int(i) for i in selection.get("Fleets", [])]

        all_released_legions = list(
            Legion.objects.filter(game=game_id, released_by_rebel=True).order_by("number")
        )
        all_released_fleets = list(
            Fleet.objects.filter(game=game_id, released_by_rebel=True).order_by("number")
        )

        all_released_legion_ids = {l.id for l in all_released_legions}
        all_released_fleet_ids = {f.id for f in all_released_fleets}

        if any(i not in all_released_legion_ids for i in legion_ids):
            return ExecutionResult(False, "Invalid legions selected.")
        if any(i not in all_released_fleet_ids for i in fleet_ids):
            return ExecutionResult(False, "Invalid fleets selected.")

        total_cost = (len(legion_ids) + len(fleet_ids)) * 2
        if total_cost > game.state_treasury:
            return ExecutionResult(False, "The State cannot afford to maintain these forces.")

        maintained_legions = [l for l in all_released_legions if l.id in legion_ids]
        eliminated_legions = [l for l in all_released_legions if l.id not in legion_ids]
        maintained_fleets = [f for f in all_released_fleets if f.id in fleet_ids]
        eliminated_fleets = [f for f in all_released_fleets if f.id not in fleet_ids]

        game.state_treasury -= total_cost

        for legion in maintained_legions:
            legion.released_by_rebel = False
        Legion.objects.bulk_update(maintained_legions, ["released_by_rebel"])

        for fleet in maintained_fleets:
            fleet.released_by_rebel = False
        Fleet.objects.bulk_update(maintained_fleets, ["released_by_rebel"])

        for legion in eliminated_legions:
            legion.delete()
        for fleet in eliminated_fleets:
            fleet.delete()

        if maintained_legions or maintained_fleets:
            Log.create_object(
                game_id,
                f"The State paid {total_cost}T to maintain "
                f"{unit_list_to_string(maintained_legions, maintained_fleets)}.",
            )
        if eliminated_legions or eliminated_fleets:
            Log.create_object(
                game_id,
                f"{unit_list_to_string(eliminated_legions, eliminated_fleets)} were eliminated.",
            )

        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()
        game.sub_phase = Game.SubPhase.REDISTRIBUTION
        game.save()

        return ExecutionResult(True)
