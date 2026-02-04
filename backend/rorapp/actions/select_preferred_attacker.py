from typing import Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import AvailableAction, Faction, Game, Senator


class SelectPreferredAttackerAction(ActionBase):
    NAME = "Select preferred attacker"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.RESOLUTION
            and not faction.has_status_item(FactionStatusItem.DONE)
            and any(
                c.imminent and c.commander and c.commander.faction == faction
                for c in game_state.campaigns
            )
        ):
            return faction
        return None

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:

        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        commanders = [
            c.commander for c in snapshot.campaigns if c.commander and c.imminent
        ]
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Preferred attacker",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                            }
                            for s in commanders
                        ],
                    },
                ],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, str],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:

        preferred_attacker = [
            s
            for s in Senator.objects.filter(game=game_id)
            if s.id == int(selection["Preferred attacker"])
        ][0]
        if not preferred_attacker:
            return ExecutionResult(False)

        preferred_attacker.add_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
        preferred_attacker.save()

        faction = Faction.objects.get(id=faction_id)
        faction.add_status_item(FactionStatusItem.DONE)
        faction.save()

        return ExecutionResult(True)
