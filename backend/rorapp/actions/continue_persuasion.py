from typing import Any, Dict, Optional, List

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.persuasion_success_chance import persuasion_success_chance
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class ContinuePersuasionAction(ActionBase):
    NAME = "Continue persuasion"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if not (
            faction
            and game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PERSUASION_DECISION
        ):
            return None
        if any(
            s.has_status_item(Senator.StatusItem.PERSUADER)
            for s in game_state.senators
            if s.faction and s.faction.id == faction.id
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
        additional_bribe = int(selection.get("Talents", 0))
        if additional_bribe < 0:
            return ExecutionResult(False, "Invalid bribe amount.")

        game = Game.objects.get(id=game_id)

        persuading_senator = next(
            (
                s
                for s in Senator.objects.filter(game=game_id, alive=True)
                if s.has_status_item(Senator.StatusItem.PERSUADER)
            ),
            None,
        )
        target = next(
            (
                s
                for s in Senator.objects.filter(game=game_id, alive=True)
                if s.has_status_item(Senator.StatusItem.PERSUASION_TARGET)
            ),
            None,
        )
        if not persuading_senator or not target:
            return ExecutionResult(False, "Persuasion state is invalid.")

        persuading_faction = persuading_senator.faction
        if not persuading_faction:
            return ExecutionResult(False, "Invalid persuading faction.")

        if additional_bribe > 0:
            if persuading_senator.talents < additional_bribe:
                return ExecutionResult(False, "Not enough talents.")
            can_bribe = any(
                f.has_status_item(FactionStatusItem.COUNTER_BRIBED)
                for f in Faction.objects.filter(game=game_id)
            )
            if not can_bribe:
                return ExecutionResult(
                    False, "Cannot raise the bribe when no counter-bribe was made."
                )
            persuading_senator.talents -= additional_bribe
            target.talents += additional_bribe
            new_total = (persuading_senator.get_bribe_amount() or 0) + additional_bribe
            persuading_senator.set_bribe_amount(new_total)
            persuading_senator.save()
            target.save()
            threshold = 9 if game.era_ends else 10
            modifier = (
                persuading_senator.oratory
                + persuading_senator.influence
                - target.loyalty
                - target.talents
                + 2 * new_total
                - (7 if target.faction_id else 0)
            )
            chance = persuasion_success_chance(modifier, threshold)
            Log.create_object(
                game_id,
                f"{persuading_senator.display_name} bribed {additional_bribe}T ({chance}% success chance).",
            )
            game.sub_phase = Game.SubPhase.PERSUASION_COUNTER_BRIBE
            game.save()
            return ExecutionResult(True)

        persuading_senator.refresh_from_db()
        target.refresh_from_db()

        total_bribe = persuading_senator.get_bribe_amount() or 0
        modifier = (
            persuading_senator.oratory
            + persuading_senator.influence
            + 2 * total_bribe
            - target.loyalty
            - target.talents
            - (7 if target.faction_id else 0)
        )

        roll = random_resolver.roll_dice() + random_resolver.roll_dice()
        threshold = 9 if game.era_ends else 10
        success = roll <= modifier and roll < threshold

        if success:
            message = f"{persuading_senator.display_name} successfully persuaded {target.display_name} to"
            if target.faction:
                message += f" leave {target.faction.display_name} and"
            message += f" join {persuading_faction.display_name}."
            Log.create_object(game_id, message)
            target.faction = persuading_faction
            target.save()
        else:
            Log.create_object(
                game_id,
                f"{persuading_senator.display_name} failed to persuade {target.display_name}.",
            )

        for s in Senator.objects.filter(game=game_id):
            s.remove_status_item(Senator.StatusItem.PERSUADER)
            s.remove_status_item(Senator.StatusItem.PERSUASION_TARGET)
            s.set_bribe_amount(None)
            s.save()

        for f in Faction.objects.filter(game=game_id):
            f.remove_status_item(FactionStatusItem.COUNTER_BRIBED)
            f.remove_status_item(FactionStatusItem.SKIPPED)
            f.save()

        game.sub_phase = Game.SubPhase.ATTRACT_KNIGHT
        game.save()

        return ExecutionResult(True)
