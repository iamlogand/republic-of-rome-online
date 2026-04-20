from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class SkipAction(ActionBase):
    NAME = "Skip"
    POSITION = 101

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None

        match (game_state.game.phase, game_state.game.sub_phase):
            case (Game.Phase.FORUM, Game.SubPhase.PERSUASION_ATTEMPT) | (
                Game.Phase.FORUM,
                Game.SubPhase.ATTRACT_KNIGHT,
            ):
                if faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE):
                    return faction

            case (Game.Phase.FORUM, Game.SubPhase.SPONSOR_GAMES):
                if faction.has_status_item(
                    FactionStatusItem.CURRENT_INITIATIVE
                ) and any(
                    s.talents >= 7
                    for s in game_state.senators
                    if s.faction and s.faction.id == faction.id and s.alive
                ):
                    return faction

            case (Game.Phase.FORUM, Game.SubPhase.INITIATIVE_AUCTION):
                if faction.has_status_item(FactionStatusItem.CURRENT_BIDDER):
                    return faction

            case (Game.Phase.FORUM, Game.SubPhase.PERSUASION_COUNTER_BRIBE):
                if faction.has_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER):
                    return faction

            case (Game.Phase.SENATE, Game.SubPhase.DICTATOR_APPOINTMENT):
                if (
                    not faction.has_status_item(FactionStatusItem.SKIPPED)
                    and not faction.has_status_item(FactionStatusItem.DONE)
                    and any(
                        s
                        for s in game_state.senators
                        if s.faction
                        and s.faction.id == faction.id
                        and (
                            s.has_title(Senator.Title.ROME_CONSUL)
                            or s.has_title(Senator.Title.FIELD_CONSUL)
                        )
                    )
                ):
                    return faction

            case (Game.Phase.SENATE, Game.SubPhase.DICTATOR_ELECTION):
                if (
                    game_state.game.current_proposal is None
                    or game_state.game.current_proposal == ""
                ) and any(
                    s
                    for s in game_state.senators
                    if s.faction
                    and s.faction.id == faction.id
                    and s.has_title(Senator.Title.PRESIDING_MAGISTRATE)
                ) and not any(
                    f
                    for f in game_state.factions
                    if f.id != faction.id
                    and f.has_status_item(FactionStatusItem.PLAYED_TRIBUNE)
                ):
                    return faction

        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if faction:
            return [
                AvailableAction.objects.create(
                    game=snapshot.game,
                    faction=faction,
                    base_name=self.NAME,
                    position=self.POSITION,
                    schema=[],
                )
            ]
        return []

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        game = Game.objects.get(id=game_id)

        match (game.phase, game.sub_phase):
            case (Game.Phase.FORUM, Game.SubPhase.PERSUASION_ATTEMPT):
                game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT

            case (Game.Phase.FORUM, Game.SubPhase.ATTRACT_KNIGHT):
                game.sub_phase = Game.SubPhase.SPONSOR_GAMES

            case (Game.Phase.FORUM, Game.SubPhase.SPONSOR_GAMES):
                game.sub_phase = Game.SubPhase.FACTION_LEADER

            case (Game.Phase.FORUM, Game.SubPhase.INITIATIVE_AUCTION):
                faction = Faction.objects.get(game=game_id, id=faction_id)
                faction.add_status_item(FactionStatusItem.SKIPPED)
                faction.save()

            case (Game.Phase.FORUM, Game.SubPhase.PERSUASION_COUNTER_BRIBE):
                faction = Faction.objects.get(game=game_id, id=faction_id)
                faction.add_status_item(FactionStatusItem.SKIPPED)
                faction.save()

            case (Game.Phase.SENATE, Game.SubPhase.DICTATOR_APPOINTMENT):
                faction = Faction.objects.get(game=game_id, id=faction_id)
                faction.add_status_item(FactionStatusItem.SKIPPED)
                faction.save()
                Log.create_object(
                    game_id,
                    f"{faction.display_name} declined to nominate a Dictator.",
                )

            case (Game.Phase.SENATE, Game.SubPhase.DICTATOR_ELECTION):
                faction = Faction.objects.get(game=game_id, id=faction_id)
                # Clear any played-tribune status
                faction.remove_status_item(FactionStatusItem.PLAYED_TRIBUNE)
                faction.save()
                # Clear PROPOSED_VIA_TRIBUNE from all factions
                factions = list(Faction.objects.filter(game=game_id))
                for f in factions:
                    f.remove_status_item(FactionStatusItem.PROPOSED_VIA_TRIBUNE)
                Faction.objects.bulk_update(factions, ["status_items"])
                Log.create_object(
                    game_id,
                    "The presiding magistrate declined to call for a Dictator election.",
                )
                game.sub_phase = Game.SubPhase.CENSOR_ELECTION
                game.clear_senate_sub_phase_proposals()

        game.save()
        return ExecutionResult(True)
