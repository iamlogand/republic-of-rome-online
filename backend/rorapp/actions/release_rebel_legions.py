from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.text import pluralize
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import AvailableAction, Campaign, Faction, Game, Legion, Log, Senator, War


class ReleaseRebelLegionsAction(ActionBase):
    NAME = "Release rebel legions"
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
            and game_state.game.sub_phase == Game.SubPhase.REBEL_LEGIONS_RELEASE
            and game_state.game.rebel_legions_to_release > 0
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
                            snapshot.game.rebel_legions_to_release,
                            len(chargeable_legions),
                        ),
                    },
                ],
                context={"legions_to_release": snapshot.game.rebel_legions_to_release},
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
        chargeable_ids = {l.id for l in chargeable_legions}

        legion_ids = [int(i) for i in selection.get("Legions", [])]

        if len(legion_ids) != game.rebel_legions_to_release:
            return ExecutionResult(
                False,
                f"Select exactly {pluralize(game.rebel_legions_to_release, 'legion')} to release.",
            )
        if any(i not in chargeable_ids for i in legion_ids):
            return ExecutionResult(False, "Invalid legion selected.")

        released_legions = [l for l in chargeable_legions if l.id in legion_ids]

        for legion in released_legions:
            legion.campaign = None
            legion.released_by_rebel = True
        Legion.objects.bulk_update(released_legions, ["campaign", "released_by_rebel"])

        Log.create_object(
            game_id,
            f"{primary_rebel.display_name} released {unit_list_to_string(released_legions, [])},"
            f" which returned to the reserve forces.",
        )

        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()
        game.rebel_legions_to_release = 0

        if released_legions:
            hrao = next(
                (s for s in Senator.objects.filter(game=game_id, alive=True)
                 if s.has_title(Senator.Title.HRAO)),
                None,
            )
            if hrao and hrao.faction_id:
                hrao_faction = Faction.objects.get(id=hrao.faction_id)
                hrao_faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
                hrao_faction.save()
                game.sub_phase = Game.SubPhase.RELEASED_LEGIONS_DISBANDMENT
            else:
                game.sub_phase = Game.SubPhase.REDISTRIBUTION
        else:
            game.sub_phase = Game.SubPhase.REDISTRIBUTION

        game.save()
        return ExecutionResult(True)
