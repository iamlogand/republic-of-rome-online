from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class SkipDictatorAppointmentAction(ActionBase):
    NAME = "Skip"
    POSITION = 101

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.DICTATOR_APPOINTMENT
            and not faction.has_status_item(FactionStatusItem.SKIPPED)
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
                    field_descriptors=[],
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
        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.add_status_item(FactionStatusItem.SKIPPED)
        faction.save()
        Log.create_object(
            game_id,
            f"{faction.display_name} declined to nominate a Dictator.",
        )
        game.save()
        return ExecutionResult(True)
