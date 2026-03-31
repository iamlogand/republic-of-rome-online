from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Campaign, Faction, Game, Log, Senator


class AttackLandForcesAction(ActionBase):
    NAME = "Fight land battle"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        if game_state.game.phase != Game.Phase.COMBAT:
            return None
        if game_state.game.sub_phase != Game.SubPhase.RESOLUTION:
            return None

        faction = game_state.get_faction(faction_id)
        if faction and any(
            s
            for s in game_state.senators
            if s.faction
            and s.faction.id == faction.id
            and s.has_status_item(Senator.StatusItem.CONSIDERING_LAND_BATTLE)
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
        faction = Faction.objects.get(game=game_id, id=faction_id)
        if not faction:
            return ExecutionResult(False)

        for senator in faction.senators.all():
            if senator.has_status_item(Senator.StatusItem.CONSIDERING_LAND_BATTLE):
                senator.remove_status_item(Senator.StatusItem.CONSIDERING_LAND_BATTLE)
                senator.save()

                campaign = Campaign.objects.filter(
                    game=game_id, commander=senator
                ).first()
                if campaign:
                    campaign.pending = True
                    campaign.save()

                Log.create_object(
                    game_id,
                    f"{senator.display_name} pressed the attack against the land forces.",
                )

        return ExecutionResult(True)
