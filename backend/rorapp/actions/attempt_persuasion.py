from typing import Any, Dict, Optional, List

from rorapp.actions.meta.action_base import ActionBase
from rorapp.actions.meta.execution_result import ExecutionResult
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.game_state.game_state_live import GameStateLive
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.persuasion_success_chance import persuasion_success_chance
from rorapp.helpers.resolve_persuasion import resolve_persuasion
from rorapp.models import AvailableAction, Faction, Game, Log, Senator


class AttemptPersuasionAction(ActionBase):
    NAME = "Attempt persuasion"
    POSITION = 0

    def is_allowed(
        self, game_state: GameStateLive | GameStateSnapshot, faction_id: int
    ) -> Optional[Faction]:
        faction = game_state.get_faction(faction_id)
        if (
            faction
            and game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PERSUASION_ATTEMPT
            and faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE)
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
        persuading_senator_id = selection["Persuader"]
        target_senator_id = selection["Target"]
        initial_bribe = int(selection["Talents"])
        use_seduction = bool(selection.get("Seduction", False))
        use_blackmail = bool(selection.get("Blackmail", False))

        if initial_bribe < 0:
            return ExecutionResult(False, "Invalid bribe amount.")

        if use_seduction and use_blackmail:
            return ExecutionResult(False, "Cannot use both Seduction and Blackmail.")

        persuader = Senator.objects.get(game=game_id, id=persuading_senator_id)
        target = Senator.objects.get(game=game_id, id=target_senator_id)

        persuader_faction = persuader.faction
        if not persuader_faction or persuader_faction.id != faction_id:
            return ExecutionResult(False, "Invalid persuader faction.")

        if use_seduction and not persuader_faction.has_card("seduction"):
            return ExecutionResult(False, "No Seduction card in hand.")
        if use_blackmail and not persuader_faction.has_card("blackmail"):
            return ExecutionResult(False, "No Blackmail card in hand.")

        if persuader.talents < initial_bribe:
            return ExecutionResult(False, "Not enough talents.")

        game = Game.objects.get(id=game_id)
        threshold = 9 if game.era_ends else 10
        modifier = (
            persuader.oratory
            + persuader.influence
            + initial_bribe
            - target.loyalty
            - target.talents
            - (7 if target.faction_id else 0)
        )
        if persuasion_success_chance(modifier, threshold) == 0:
            return ExecutionResult(
                False, "No chance of success with this bribe amount."
            )

        if use_seduction:
            persuader_faction.remove_card("seduction")
        if use_blackmail:
            persuader_faction.remove_card("blackmail")
        if use_seduction or use_blackmail:
            persuader_faction.save()

        # Transfer initial bribe immediately to target
        persuader.talents -= initial_bribe
        target.talents += initial_bribe

        persuader.add_status_item(Senator.StatusItem.PERSUADER)
        if initial_bribe > 0:
            persuader.set_bribe_amount(initial_bribe)
        target.add_status_item(Senator.StatusItem.PERSUASION_TARGET)
        persuader.save()
        target.save()

        message = f"{persuader.display_name} of {persuader_faction.display_name} began a persuasion attempt targeting"
        message += (
            f" {target.display_name} of {target.faction.display_name}"
            if target.faction
            else f" the unaligned senator {target.display_name}"
        )
        chance = persuasion_success_chance(modifier, threshold)
        if initial_bribe:
            unopposed = use_seduction or use_blackmail
            intro = "with a" if unopposed else "starting with an initial"
            message += f", {intro} bribe of {initial_bribe}T"
        message += f" ({chance}% success chance)."
        if use_seduction:
            message += " Seduction was used to prevent counter-bribes."
        elif use_blackmail:
            message += " Blackmail was used to prevent counter-bribes."
        Log.create_object(game_id, message)

        if use_seduction or use_blackmail:
            try:
                resolve_persuasion(
                    game_id, persuader, target, use_blackmail, random_resolver
                )
            except ValueError as e:
                return ExecutionResult(False, str(e))
        else:
            game.sub_phase = Game.SubPhase.PERSUASION_COUNTER_BRIBE
            game.save()

        return ExecutionResult(True)
