from typing import Any, Dict, Optional, List
from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.dictator_candidates import get_eligible_master_of_horse_candidates
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class SelectMasterOfHorseAction(ActionBase):
    NAME = "Select Master of Horse"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not faction:
            return None
        if not (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.MASTER_OF_HORSE_APPOINTMENT
        ):
            return None
        # Faction must control the Dictator senator
        has_dictator = any(
            s
            for s in game_state.senators
            if s.faction
            and s.faction.id == faction.id
            and s.has_title(Senator.Title.DICTATOR)
        )
        if not has_dictator:
            return None
        return faction

    def get_schema(
        self, snapshot: GameStateSnapshot, faction_id: int
    ) -> List[AvailableAction]:
        faction = self.is_allowed(snapshot, faction_id)
        if not faction:
            return []

        dictator = next(
            s for s in snapshot.senators if s.has_title(Senator.Title.DICTATOR)
        )
        candidates = sorted(
            get_eligible_master_of_horse_candidates(snapshot.senators, dictator.id),
            key=lambda s: s.family_name,
        )

        return [
            AvailableAction.objects.create(
                game=snapshot.game,
                faction=faction,
                base_name=self.NAME,
                position=self.POSITION,
                schema=[
                    {
                        "type": "select",
                        "name": "Master of Horse",
                        "options": [
                            {
                                "value": s.id,
                                "object_class": "senator",
                                "id": s.id,
                            }
                            for s in candidates
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
        game = Game.objects.get(id=game_id)
        senator_id = selection["Master of Horse"]
        master_of_horse = Senator.objects.get(id=senator_id)

        master_of_horse.add_title(Senator.Title.MASTER_OF_HORSE)
        master_of_horse.influence += 3
        master_of_horse.save()

        if master_of_horse.faction:
            Log.create_object(
                game_id,
                f"{master_of_horse.display_name} of {master_of_horse.faction.display_name} was appointed Master of Horse. He gained 3 influence.",
            )

        game.sub_phase = Game.SubPhase.CENSOR_ELECTION
        game.clear_defeated_proposals()
        game.save()

        return ExecutionResult(True)
