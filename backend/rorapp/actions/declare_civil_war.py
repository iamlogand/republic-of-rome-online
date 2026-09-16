from typing import Any, Dict, List, Optional

from django.conf import settings

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import declaring_campaign, revolt_available
from rorapp.helpers.declare_civil_war import declare_civil_war
from rorapp.models import AvailableAction, Faction


class DeclareCivilWarAction(ActionBase):
    NAME = "Declare civil war"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        if not settings.FEATURE_FLAGS.get("civil_war"):
            return None
        campaign = declaring_campaign(game_state, faction_id)
        if not campaign or not revolt_available(game_state, campaign):
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
        game_state = GameStateLive(game_id)
        campaign = declaring_campaign(game_state, faction_id)
        if not campaign:
            return ExecutionResult(False, "It is not your commander's decision.")
        if not revolt_available(game_state, campaign):
            return ExecutionResult(
                False, "Another faction is already in revolt with a stronger army."
            )

        declare_civil_war(campaign)
        return ExecutionResult(True)
