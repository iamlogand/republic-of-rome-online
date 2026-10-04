from typing import Any, Dict, List, Optional

from django.conf import settings

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.revolt import (
    declaring_campaign,
    legions_to_sway,
    revolt_available,
)
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Campaign, Faction, Legion, Log, Senator

# A legion follows its commander into revolt on a 5 or 6 (1.11.31)
FOLLOW_TARGET = 5


def _paymasters(
    game_state: GameStateLive | GameStateSnapshot, campaign: Campaign
) -> List[Senator]:
    """The commander, and his Master of Horse if the same player consents for both (1.11.31)."""

    commander = campaign.commander
    if not commander:
        return []
    master_of_horse = (
        game_state.get_senator(campaign.master_of_horse_id)
        if campaign.master_of_horse_id
        else None
    )
    if master_of_horse and master_of_horse.faction_id == commander.faction_id:
        return [commander, master_of_horse]
    return [commander]


class SwayTheLegionsAction(ActionBase):
    NAME = "Sway the legions"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        if not settings.FEATURE_FLAGS.get("civil_war"):
            return None
        campaign = declaring_campaign(game_state, faction_id)
        if (
            not campaign
            or not campaign.commander
            or campaign.commander.has_status_item(Senator.StatusItem.SWAYED_LEGIONS)
            or not revolt_available(game_state, campaign)
            or not legions_to_sway(game_state, campaign)
        ):
            return None
        return game_state.get_faction(faction_id)

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        campaign = declaring_campaign(snapshot, faction_id)
        if not faction or not campaign:
            return []

        legions = legions_to_sway(snapshot, campaign)
        talents = sum(s.talents for s in _paymasters(snapshot, campaign))
        chance = round((7 - FOLLOW_TARGET) / 6 * 100)
        chance_bribed = round((7 - FOLLOW_TARGET + 1) / 6 * 100)
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
                ],
                context={
                    "talents": talents,
                    "chance": chance,
                    "chance_bribed": chance_bribed,
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
        game_state = GameStateLive(game_id)
        campaign = declaring_campaign(game_state, faction_id)
        if not campaign or not campaign.commander:
            return ExecutionResult(False, "It is not your commander's decision.")
        commander = campaign.commander

        legions = legions_to_sway(game_state, campaign)
        bribed_ids = [int(i) for i in selection.get("Legions to bribe", [])]
        bribed = [l for l in legions if l.id in bribed_ids]
        if len(bribed) != len(bribed_ids):
            return ExecutionResult(False, "Invalid legions selected.")

        paymasters = _paymasters(game_state, campaign)
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
            if random_resolver.roll_dice(1) + modifier < FOLLOW_TARGET:
                deserters.append(legion)

        followers = sorted(
            (
                l
                for l in game_state.legions
                if l.campaign_id == campaign.id and l not in deserters
            ),
            key=lambda l: l.number,
        )
        for legion in deserters:
            legion.campaign = None
        Legion.objects.bulk_update(deserters, ["campaign"])

        commander.add_status_item(Senator.StatusItem.SWAYED_LEGIONS)
        commander.save()

        text = f"{commander.display_name} attempted to sway his legions"
        if bribed:
            text += f", spending {len(bribed)}T"
        if not deserters:
            text += ". All agreed to follow him."
        elif not followers:
            text += ". All refused to follow him and returned to the reserve forces."
        else:
            text += (
                f". {unit_list_to_string(followers, [])} agreed to follow him "
                f"while {unit_list_to_string(deserters, [])} refused and returned "
                "to the reserve forces."
            )
        Log.create_object(game_id, text)

        return ExecutionResult(True)
