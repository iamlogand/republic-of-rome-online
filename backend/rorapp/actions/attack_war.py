from typing import Any, Dict, List, Optional

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import standing_rebel
from rorapp.helpers.rebel_end_game import active_wars_against_rome, rebel_campaign
from rorapp.helpers.resolve_combat import resolve_combat
from rorapp.models import AvailableAction, Faction, Game, War


class AttackWarAction(ActionBase):
    NAME = "Attack war"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction or not (
            game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.REBEL_END_GAME
        ):
            return None
        rebel = standing_rebel(faction.game_id)
        if not rebel or not rebel.alive or rebel.faction_id != faction.id:
            return None
        if not active_wars_against_rome(faction.game_id):
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []
        wars = active_wars_against_rome(snapshot.game.id)
        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                field_descriptors=[
                    {
                        "type": "select",
                        "name": "War",
                        "options": [
                            {"value": w.id, "object_class": "war", "id": w.id}
                            for w in wars
                        ],
                    }
                ],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        rebel = standing_rebel(game_id)
        campaign = rebel_campaign(game_id)
        if not rebel or not rebel.alive or rebel.faction_id != faction_id:
            return ExecutionResult(False, "There is no rebel army to attack with.")
        if not campaign:
            return ExecutionResult(False, "There is no rebel army to attack with.")

        war = War.objects.filter(
            game=game_id, id=int(selection["War"]), status=War.Status.ACTIVE
        ).first()
        if not war or war.primary_rebel_id:
            return ExecutionResult(False, "Invalid war selected.")

        if campaign.fleets.count() < war.fleet_support:
            return ExecutionResult(
                False, "There are not enough fleets to support the attack."
            )

        campaign.war = war
        campaign.land_victory = False
        campaign.save()
        resolve_combat(game_id, campaign.id, random_resolver)
        return ExecutionResult(True)
