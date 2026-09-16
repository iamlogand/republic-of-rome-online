from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.game_data import is_war_card
from rorapp.helpers.new_alliance import apply_new_alliance
from rorapp.models import AvailableAction, Faction, Game, War


class ResolveNewAllianceAction(ActionBase):
    NAME = "Resolve new alliance"
    POSITION = 0
    WAR_FIELD = "War"

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.NEW_ALLIANCE
            and faction.has_status_item(FactionStatusItem.AWAITING_DECISION)
        ):
            return faction
        return None

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
                field_descriptors=[
                    {
                        "type": "select",
                        "name": self.WAR_FIELD,
                        "options": [
                            {"value": w.id, "object_class": "war", "id": w.id}
                            for w in snapshot.wars
                            if is_war_card(w.name)
                        ],
                    }
                ],
                context={
                    "another": snapshot.game.count_effect(GameEffect.NEW_ALLIANCE)
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
        game = Game.objects.get(id=game_id)
        war = (
            War.objects.filter(game=game, id=selection[self.WAR_FIELD])
            .exclude(status=War.Status.DEFEATED)
            .first()
        )
        if war is None or not is_war_card(war.name):
            return ExecutionResult(False, "Select a war.")

        apply_new_alliance(game, war, random_resolver)

        faction = Faction.objects.get(game=game, id=faction_id)
        faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
        faction.save()
        game.sub_phase = Game.SubPhase.END
        game.save()

        return ExecutionResult(True)
