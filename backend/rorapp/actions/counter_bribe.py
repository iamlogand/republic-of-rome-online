from typing import Any, Dict, Optional, List

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.persuasion_success_chance import persuasion_success_chance
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class CounterBribeAction(ActionBase):
    NAME = "Counter-bribe"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PERSUASION_COUNTER_BRIBE
            and faction.has_status_item(FactionStatusItem.CURRENT_COUNTER_BRIBER)
            and faction.treasury > 0
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
                schema=[],
            )
        ]

    def execute(
        self,
        game_id: int,
        faction_id: int,
        selection: Dict[str, Any],
        random_resolver: RandomResolver,
    ) -> ExecutionResult:
        talents = int(selection["Talents"])
        if talents < 1:
            return ExecutionResult(False, "Must spend at least 1 talent.")

        faction = Faction.objects.get(game=game_id, id=faction_id)
        if faction.treasury < talents:
            return ExecutionResult(False, "Not enough talents in faction treasury.")

        target = next(
            (
                s
                for s in Senator.objects.filter(game=game_id, alive=True)
                if s.has_status_item(Senator.StatusItem.PERSUASION_TARGET)
            ),
            None,
        )
        if not target:
            return ExecutionResult(False, "No persuasion target found.")

        persuader = next(
            (
                s
                for s in Senator.objects.filter(game=game_id, alive=True)
                if s.has_status_item(Senator.StatusItem.PERSUADER)
            ),
            None,
        )

        faction.treasury -= talents
        target.talents += talents
        faction.add_status_item(FactionStatusItem.COUNTER_BRIBED)
        faction.save()
        target.save()

        game = Game.objects.get(id=game_id)
        threshold = 9 if game.era_ends else 10
        total_bribe = (persuader.get_bribe_amount() or 0) if persuader else 0
        modifier = (
            persuader.oratory
            + persuader.influence
            + 2 * total_bribe
            - target.loyalty
            - target.talents
            - (7 if target.faction_id else 0)
            if persuader
            else 0
        )
        chance = persuasion_success_chance(modifier, threshold)

        Log.create_object(
            game_id,
            f"{faction.display_name} counter-bribed {talents}T ({chance}% success chance).",
        )

        return ExecutionResult(True)
