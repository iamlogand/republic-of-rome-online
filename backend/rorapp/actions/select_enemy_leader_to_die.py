from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.enemy_leader_dies import resolve_enemy_leader_dies
from rorapp.models import AvailableAction, EnemyLeader, Faction, Game, Senator


class SelectEnemyLeaderToDieAction(ActionBase):
    NAME = "Select enemy leader to die"
    POSITION = 0
    LEADER_FIELD = "Enemy leader"

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if not (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.ENEMY_LEADER_DIES
        ):
            return None
        hrao = next(
            (s for s in game_state.senators if s.has_title(Senator.Title.HRAO)), None
        )
        if not hrao or hrao.faction_id != faction.id:
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        leaders = EnemyLeader.objects.filter(game=snapshot.game.id).order_by("id")
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {
                        "type": "select",
                        "name": self.LEADER_FIELD,
                        "options": [{"value": l.id, "name": l.name} for l in leaders],
                    }
                ],
                context={
                    "sues_for_peace": snapshot.game.count_effect(
                        GameEffect.ENEMY_LEADER_DIES
                    )
                    > 1
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
        leader_id = str(selection.get(self.LEADER_FIELD))
        leader = (
            EnemyLeader.objects.filter(game=game_id, id=leader_id).first()
            if leader_id.isdecimal()
            else None
        )
        if not leader:
            return ExecutionResult(False, "Select an enemy leader.")

        game = Game.objects.get(id=game_id)
        resolve_enemy_leader_dies(game, leader, random_resolver)
        game.phase = Game.Phase.POPULATION
        game.sub_phase = Game.SubPhase.START
        game.save()
        return ExecutionResult(True)
