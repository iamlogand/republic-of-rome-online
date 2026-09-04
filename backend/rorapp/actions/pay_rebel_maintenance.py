from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import refresh_civil_war_strength
from rorapp.helpers.rebel_maintenance import (
    MAINTENANCE_COST,
    payable_rebel_legions,
    rebel_faction,
    rebel_paymasters,
)
from rorapp.helpers.text import pluralize
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Faction, Game, Legion, Log, Senator


class PayRebelMaintenanceAction(ActionBase):
    NAME = "Pay rebel maintenance"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction or not (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REBEL_MAINTENANCE
        ):
            return None
        rebels_faction = rebel_faction(faction.game_id)
        if not rebels_faction or rebels_faction.id != faction.id:
            return None
        if not payable_rebel_legions(faction.game_id):
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        game_id = snapshot.game.id
        legions = payable_rebel_legions(game_id)
        paymasters = rebel_paymasters(game_id)
        personal = sum(s.talents for s in paymasters)
        affordable = min(len(legions), (personal + faction.treasury) // MAINTENANCE_COST)
        must_release = len(legions) - affordable

        field_descriptors: List[Dict[str, Any]] = [
            {
                "type": "number",
                "name": "Talents from the faction treasury",
                "min": [0],
                "max": [faction.treasury, affordable * MAINTENANCE_COST],
            }
        ]
        if must_release > 0:
            field_descriptors.append(
                {
                    "type": "multiselect",
                    "name": "Legions to release",
                    "options": [
                        {"value": l.id, "object_class": "legion", "id": l.id}
                        for l in legions
                    ],
                }
            )

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=field_descriptors,
                context={
                    "legions": len(legions),
                    "cost": len(legions) * MAINTENANCE_COST,
                    "must_release": must_release,
                },
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        faction = rebel_faction(game_id)
        if not faction or faction.id != faction_id:
            return ExecutionResult(False, "There is no rebel maintenance to pay.")

        legions = payable_rebel_legions(game_id)
        paymasters = rebel_paymasters(game_id)
        personal = sum(s.talents for s in paymasters)
        affordable = min(len(legions), (personal + faction.treasury) // MAINTENANCE_COST)
        must_release = len(legions) - affordable

        released_ids = [int(i) for i in selection.get("Legions to release", [])]
        released = [l for l in legions if l.id in released_ids]
        if len(released) != len(released_ids):
            return ExecutionResult(False, "Invalid legions selected.")
        if len(released) != must_release:
            return ExecutionResult(
                False,
                f"{pluralize(must_release, 'legion')} must be released, "
                "no more and no fewer.",
            )

        owed = affordable * MAINTENANCE_COST
        from_treasury = int(selection.get("Talents from the faction treasury", 0))
        if from_treasury < 0 or from_treasury > faction.treasury:
            return ExecutionResult(False, "The faction treasury cannot pay that much.")
        if from_treasury > owed:
            return ExecutionResult(False, "That is more than the maintenance costs.")
        if owed - from_treasury > personal:
            return ExecutionResult(
                False, "The rebels cannot cover the rest of the maintenance."
            )

        faction.treasury -= from_treasury
        faction.save()
        owed_personally = owed - from_treasury
        for paymaster in paymasters:
            payment = min(owed_personally, paymaster.talents)
            paymaster.talents -= payment
            paymaster.save()
            owed_personally -= payment

        if owed > 0:
            Log.create_object(
                game_id,
                f"{paymasters[0].display_name} paid {owed}T to maintain "
                f"{pluralize(affordable, 'rebel legion')}.",
            )

        if released:
            for legion in released:
                legion.campaign = None
                legion.released = True
            Legion.objects.bulk_update(released, ["campaign", "released"])
            refresh_civil_war_strength(game_id)
            Log.create_object(
                game_id,
                f"{paymasters[0].display_name} could not maintain "
                f"{unit_list_to_string(released, [])}, which were released to "
                "the Senate.",
            )

        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()
        return ExecutionResult(True)
