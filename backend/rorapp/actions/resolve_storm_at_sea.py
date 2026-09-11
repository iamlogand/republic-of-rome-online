from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.storm_at_sea import (
    clear_storm_at_sea_decision,
    destroy_storm_fleets,
)
from rorapp.helpers.text import possessive
from rorapp.models import AvailableAction, Faction, Fleet, Game, Senator


class ResolveStormAtSeaAction(ActionBase):
    NAME = "Resolve storm at sea"
    POSITION = 0
    FLEETS_FIELD = "Roman fleets to eliminate"

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if game_state.game.phase != Game.Phase.FORUM:
            return None
        if game_state.game.sub_phase != Game.SubPhase.STORM_AT_SEA:
            return None
        if game_state.game.storm_at_sea_fleet_losses < 1:
            return None
        if not faction.has_status_item(FactionStatusItem.AWAITING_DECISION):
            return None

        is_hrao_faction = any(
            senator.faction_id == faction.id
            and senator.alive
            and senator.location == "Rome"
            and senator.has_title(Senator.Title.HRAO)
            for senator in game_state.senators
        )
        return faction if is_hrao_faction else None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        campaigns = {campaign.id: campaign for campaign in snapshot.campaigns}
        senators = {senator.id: senator for senator in snapshot.senators}
        wars = {war.id: war for war in snapshot.wars}

        def campaign_group(campaign_id: int) -> str:
            campaign = campaigns[campaign_id]
            commander = (
                senators.get(campaign.commander_id)
                if campaign.commander_id is not None
                else None
            )
            war = wars[campaign.war_id]
            campaign_name = (
                f"{possessive(commander.display_name)} campaign"
                if commander
                else "Uncommanded campaign"
            )
            return f"{campaign_name} — {war.name}"

        fleets = sorted(
            snapshot.fleets,
            key=lambda fleet: (
                0 if fleet.campaign_id is None else fleet.campaign_id,
                fleet.number,
            ),
        )
        options = [
            {
                "value": fleet.id,
                "name": f"Fleet {fleet.name}",
                "group": (
                    "Reserve"
                    if fleet.campaign_id is None
                    else campaign_group(fleet.campaign_id)
                ),
            }
            for fleet in fleets
        ]

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {
                        "type": "multiselect",
                        "name": self.FLEETS_FIELD,
                        "options": options,
                        "required_count": snapshot.game.storm_at_sea_fleet_losses,
                    }
                ],
                context={
                    "fleet_losses": snapshot.game.storm_at_sea_fleet_losses,
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
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game, id=faction_id)
        required_count = game.storm_at_sea_fleet_losses

        if (
            game.phase != Game.Phase.FORUM
            or game.sub_phase != Game.SubPhase.STORM_AT_SEA
            or required_count < 1
            or not faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
        ):
            return ExecutionResult(False, "No storm at sea decision is pending.")

        hrao_exists = Senator.objects.filter(
            game=game,
            faction=faction,
            alive=True,
            location="Rome",
            titles__contains=[Senator.Title.HRAO.value],
        ).exists()
        if not hrao_exists:
            return ExecutionResult(False, "Only the HRAO faction may resolve this event.")

        selected_ids = selection.get(self.FLEETS_FIELD)
        if not isinstance(selected_ids, list):
            return ExecutionResult(False, "Select the required Roman fleets.")

        fleet_ids = []
        for fleet_id in selected_ids:
            if isinstance(fleet_id, bool):
                return ExecutionResult(False, "Invalid Roman fleet selection.")
            if isinstance(fleet_id, int):
                fleet_ids.append(fleet_id)
            elif isinstance(fleet_id, str) and fleet_id.isdecimal():
                fleet_ids.append(int(fleet_id))
            else:
                return ExecutionResult(False, "Invalid Roman fleet selection.")

        if any(fleet_id < 1 for fleet_id in fleet_ids):
            return ExecutionResult(False, "Invalid Roman fleet selection.")

        if len(fleet_ids) != required_count or len(set(fleet_ids)) != required_count:
            fleet_noun = "fleet" if required_count == 1 else "fleets"
            return ExecutionResult(
                False, f"Select exactly {required_count} Roman {fleet_noun}."
            )

        fleets = list(Fleet.objects.filter(game=game, id__in=fleet_ids))
        if len(fleets) != required_count:
            return ExecutionResult(False, "One or more selected fleets no longer exist.")

        destroy_storm_fleets(game, fleets)
        clear_storm_at_sea_decision(game)
        game.sub_phase = Game.SubPhase.PERSUASION_ATTEMPT
        game.save(update_fields=["sub_phase"])

        return ExecutionResult(True)
