from typing import Any, Dict, List, Optional

from django.conf import settings

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.helpers.revolt import declaring_campaign
from rorapp.models import AvailableAction, Faction


class LayDownCommandAction(ActionBase):
    NAME = "Lay down command"
    POSITION = 6

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        if not settings.FEATURE_FLAGS.get("civil_war"):
            return None
        if not declaring_campaign(game_state, faction_id):
            return None
        return game_state.get_faction(faction_id)

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        campaign = declaring_campaign(GameStateLive(game_id), faction_id)
        if not campaign:
            return ExecutionResult(False, "It is not your commander's decision.")

        lay_down_command(campaign)
        set_hrao(game_id)

        faction = Faction.objects.get(game=game_id, id=faction_id)
        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()
        return ExecutionResult(True)
