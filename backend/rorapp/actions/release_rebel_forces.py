from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.text import pluralize
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Campaign, Faction, Fleet, Game, Legion, Log, Senator, War


class ReleaseRebelForcesAction(ActionBase):
    NAME = "Release rebel forces"
    POSITION = 0

    def _get_primary_rebel(self, game_state: GameStateLive | GameStateSnapshot) -> Optional[Senator]:
        revolt = next(
            (
                w for w in game_state.wars
                if w.primary_rebel_id is not None
            ),
            None,
        )
        if revolt is None:
            return None
        return next(
            (s for s in game_state.senators if s.id == revolt.primary_rebel_id),
            None,
        )

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if not (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REBEL_FORCES_RELEASE
            and game_state.game.rebel_units_to_release > 0
            and faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
        ):
            return None
        primary_rebel = self._get_primary_rebel(game_state)
        if not primary_rebel or primary_rebel.faction_id != faction_id:
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        primary_rebel = self._get_primary_rebel(snapshot)
        if not primary_rebel:
            return []

        rebel_campaign = next(
            (c for c in snapshot.campaigns if c.commander_id == primary_rebel.id),
            None,
        )
        if not rebel_campaign:
            return []

        chargeable_legions = sorted(
            [
                l for l in snapshot.legions
                if l.campaign_id == rebel_campaign.id
                and not (l.veteran and l.allegiance_id == primary_rebel.id)
            ],
            key=lambda l: l.number,
        )
        chargeable_fleets = sorted(
            [f for f in snapshot.fleets if f.campaign_id == rebel_campaign.id],
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
                            for l in chargeable_legions
                        ],
                        "required_count": min(
                            snapshot.game.rebel_units_to_release,
                            len(chargeable_legions),
                        ),
                    },
                    {
                        "type": "multiselect",
                        "name": "Fleets",
                        "options": [
                            {"value": f.id, "object_class": "fleet", "id": f.id}
                            for f in chargeable_fleets
                        ],
                        "inline": True,
                    },
                ],
                context={"units_to_release": snapshot.game.rebel_units_to_release},
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

        revolt = (
            War.objects.filter(game_id=game_id, primary_rebel__isnull=False)
            .exclude(status=War.Status.DEFEATED)
            .select_related("primary_rebel")
            .first()
        )
        if not revolt or not revolt.primary_rebel:
            return ExecutionResult(False, "No active revolt found.")

        primary_rebel = revolt.primary_rebel
        rebel_campaign = Campaign.objects.filter(
            game_id=game_id, commander=primary_rebel
        ).first()
        if not rebel_campaign:
            return ExecutionResult(False, "No rebel campaign found.")

        chargeable_legions = list(
            Legion.objects.filter(campaign=rebel_campaign)
            .exclude(veteran=True, allegiance=primary_rebel)
            .order_by("number")
        )
        chargeable_fleets = list(
            Fleet.objects.filter(campaign=rebel_campaign).order_by("number")
        )
        chargeable_ids = {l.id for l in chargeable_legions} | {f.id for f in chargeable_fleets}

        legion_ids = [int(i) for i in selection.get("Legions", [])]
        fleet_ids = [int(i) for i in selection.get("Fleets", [])]
        selected_ids = legion_ids + fleet_ids

        if len(selected_ids) != game.rebel_units_to_release:
            return ExecutionResult(
                False,
                f"Select exactly {pluralize(game.rebel_units_to_release, 'unit')} to release.",
            )
        if any(i not in chargeable_ids for i in selected_ids):
            return ExecutionResult(False, "Invalid unit selected.")

        released_legions = [l for l in chargeable_legions if l.id in legion_ids]
        released_fleets = [f for f in chargeable_fleets if f.id in fleet_ids]
        maintained_legions = [l for l in chargeable_legions if l.id not in legion_ids]
        maintained_fleets = [f for f in chargeable_fleets if f.id not in fleet_ids]

        for legion in released_legions:
            legion.campaign = None
            legion.released_by_rebel = True
        Legion.objects.bulk_update(released_legions, ["campaign", "released_by_rebel"])

        for fleet in released_fleets:
            fleet.campaign = None
            fleet.released_by_rebel = True
        Fleet.objects.bulk_update(released_fleets, ["campaign", "released_by_rebel"])

        paid_cost = (len(maintained_legions) + len(maintained_fleets)) * 2
        if maintained_legions or maintained_fleets:
            Log.create_object(
                game_id,
                f"{primary_rebel.display_name} spent {paid_cost}T maintaining "
                f"{unit_list_to_string(maintained_legions, maintained_fleets)}.",
            )
        if released_legions or released_fleets:
            Log.create_object(
                game_id,
                f"{unit_list_to_string(released_legions, released_fleets)} "
                f"returned to the reserve forces after {primary_rebel.display_name} "
                f"could not afford their maintenance.",
            )

        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()
        game.rebel_units_to_release = 0
        game.sub_phase = Game.SubPhase.RELEASED_FORCES_MAINTENANCE
        game.save()

        return ExecutionResult(True)
