from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Faction, Game, Legion, Log, Senator


class DisbandReleasedLegionsAction(ActionBase):
    NAME = "Disband released legions"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if not (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.RELEASED_LEGIONS_DISBANDMENT
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
        total_cost = len(released_legions) * 2

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
                            {
                                "value": l.id,
                                "object_class": "legion",
                                "id": l.id,
                                "signals": {"cost": 2},
                            }
                            for l in released_legions
                        ],
                    },
                    {
                        "type": "calculation",
                        "name": "Maintenance cost",
                        "value": f"{total_cost} - signal:cost",
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
        hrao = Senator.objects.get(
            game=game_id, alive=True, titles__contains=[Senator.Title.HRAO.value]
        )

        legion_ids = [int(i) for i in selection.get("Legions", [])]

        all_released_legions = list(
            Legion.objects.filter(game=game_id, released_by_rebel=True).order_by(
                "number"
            )
        )
        all_released_legion_ids = {l.id for l in all_released_legions}

        if any(i not in all_released_legion_ids for i in legion_ids):
            return ExecutionResult(False, "Invalid legions selected.")

        disbanded_legions = [l for l in all_released_legions if l.id in legion_ids]
        maintained_legions = [l for l in all_released_legions if l.id not in legion_ids]

        total_cost = len(maintained_legions) * 2
        if total_cost > game.state_treasury:
            return ExecutionResult(
                False, "The State cannot afford to maintain these legions."
            )

        game.state_treasury -= total_cost

        for legion in maintained_legions:
            legion.released_by_rebel = False
        Legion.objects.bulk_update(maintained_legions, ["released_by_rebel"])

        for legion in disbanded_legions:
            legion.delete()

        parts = []
        if maintained_legions:
            parts.append(f"maintain {unit_list_to_string(maintained_legions, [])} at a cost of {total_cost}T")
        if disbanded_legions:
            parts.append(f"disband {unit_list_to_string(disbanded_legions, [])}")
        Log.create_object(
            game_id, f"{hrao.display_name} had the State {' and '.join(parts)}."
        )

        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()
        game.sub_phase = Game.SubPhase.REDISTRIBUTION
        game.save()

        return ExecutionResult(True)
