from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import (
    declaring_faction,
    next_land_victor,
    rollable_legions,
)
from rorapp.helpers.text import format_list
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Faction, Legion, Log, Senator

# A legion follows its commander into revolt on a 5 or 6 (1.11.31)
LOYALTY_TARGET = 5


def _paymasters(campaign) -> List[Senator]:
    """The commander, and his Master of Horse if the same player consents for both (1.11.31)."""

    commander = campaign.commander
    paymasters = [commander] if commander else []
    master_of_horse = campaign.master_of_horse
    if (
        commander
        and master_of_horse
        and master_of_horse.faction_id == commander.faction_id
    ):
        paymasters.append(master_of_horse)
    return paymasters


class RollForLegionsAction(ActionBase):
    NAME = "Roll for legions"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = declaring_faction(game_state, faction_id)
        if not faction:
            return None
        campaign = next_land_victor(faction.game_id)
        if (
            not campaign
            or not campaign.commander
            or campaign.commander.has_status_item(Senator.StatusItem.ROLLED_FOR_LEGIONS)
            or not rollable_legions(campaign)
        ):
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []
        campaign = next_land_victor(snapshot.game.id)
        if not campaign:
            return []

        legions = rollable_legions(campaign)
        talents = sum(s.talents for s in _paymasters(campaign))
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {
                        "type": "multiselect",
                        "name": "Legions to bribe",
                        "options": [
                            {"value": l.id, "object_class": "legion", "id": l.id}
                            for l in legions
                        ],
                    },
                    {
                        "type": "chance",
                        "name": "Chance without a bribe",
                        "dice": 1,
                        "target_min": LOYALTY_TARGET,
                    },
                    {
                        "type": "chance",
                        "name": "Chance with a bribe",
                        "dice": 1,
                        "target_min": LOYALTY_TARGET,
                        "modifiers": [1],
                    },
                ],
                context={"talents": talents},
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        campaign = next_land_victor(game_id)
        if not campaign or not campaign.commander:
            return ExecutionResult(False, "There are no legions to roll for.")
        commander = campaign.commander
        if commander.faction_id != faction_id:
            return ExecutionResult(False, "It is not your commander's decision.")
        if commander.has_status_item(Senator.StatusItem.ROLLED_FOR_LEGIONS):
            return ExecutionResult(False, "These legions have already been rolled for.")

        legions = rollable_legions(campaign)
        bribed_ids = [int(i) for i in selection.get("Legions to bribe", [])]
        bribed = [l for l in legions if l.id in bribed_ids]
        if len(bribed) != len(bribed_ids):
            return ExecutionResult(False, "Invalid legions selected.")

        paymasters = _paymasters(campaign)
        if len(bribed) > sum(s.talents for s in paymasters):
            return ExecutionResult(
                False, "Not enough talents to bribe that many legions."
            )

        # Only one talent may be spent on each legion (1.11.31)
        owed = len(bribed)
        for paymaster in paymasters:
            payment = min(owed, paymaster.talents)
            paymaster.talents -= payment
            paymaster.save()
            owed -= payment

        deserters: List[Legion] = []
        for legion in legions:
            modifier = 1 if legion in bribed else 0
            if random_resolver.roll_dice(1) + modifier < LOYALTY_TARGET:
                deserters.append(legion)

        commander.add_status_item(Senator.StatusItem.ROLLED_FOR_LEGIONS)
        commander.save()

        if bribed:
            Log.create_object(
                game_id,
                f"{commander.display_name} spent {len(bribed)}T on the "
                f"loyalty of {format_list([l.name for l in bribed])}.",
            )

        if deserters:
            for legion in deserters:
                legion.campaign = None
            Legion.objects.bulk_update(deserters, ["campaign"])
            Log.create_object(
                game_id,
                f"{unit_list_to_string(deserters, [])} refused to follow "
                f"{commander.display_name} and returned to the reserve forces.",
            )
        else:
            Log.create_object(
                game_id,
                f"Every legion agreed to follow {commander.display_name}.",
            )

        return ExecutionResult(True)
