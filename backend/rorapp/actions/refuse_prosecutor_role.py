from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.models import AvailableAction, Faction, Game, Senator, Log


class RefuseProsecutorRoleAction(ActionBase):
    NAME = "Refuse prosecutor role"
    POSITION = 1

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:

        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.PROSECUTION
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and any(
                s
                for s in game_state.senators
                if s.faction
                and s.faction.id == faction.id
                and s.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
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

        senators = Senator.objects.filter(game=game_id)

        prosecutor = next(
            (
                s
                for s in senators
                if s.has_status_item(Senator.StatusItem.CONSENT_REQUIRED)
            ),
            None,
        )
        if not prosecutor:
            return ExecutionResult(False)

        prosecutor.remove_status_item(Senator.StatusItem.CONSENT_REQUIRED)
        prosecutor.save()

        accused = next(
            (s for s in senators if s.has_status_item(Senator.StatusItem.ACCUSED)),
            None,
        )
        if accused:
            accused.remove_status_item(Senator.StatusItem.ACCUSED)
            accused.save()

        Log.create_object(
            game_id,
            f"{prosecutor.display_name} refused the role of prosecutor.",
        )

        clear_proposal_and_votes(game_id)

        return ExecutionResult(True)
