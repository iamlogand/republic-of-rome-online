from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.assassination_participants import get_assassination_participants
from rorapp.helpers.assassination_proposal_consequences import (
    handle_proposal_consequences,
)
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.models import Game, Log, Senator


class ResolveAssassinationEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.ASSASSINATION_RESOLUTION
            and game_state.game.assassination_roll_result != 0
            and not any(
                f
                for f in game_state.factions
                if f.has_status_item(FactionStatusItem.AWAITING_DECISION)
            )
            and game_state.game.bodyguard_rerolls_remaining == 0
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        senators = list(Senator.objects.filter(game=game_id, alive=True))
        assassin, target = get_assassination_participants(senators)

        if assassin is None or target is None:
            self._cleanup(game, senators)
            return True

        is_caught = assassin.has_status_item(Senator.StatusItem.CAUGHT)
        roll_result = game.assassination_roll_result

        # Log the outcome now that bodyguards have had their chance
        if roll_result >= 5 and is_caught:
            Log.create_object(
                game_id,
                f"The assassination attempt succeeded, but {assassin.display_name} was caught!",
            )
        elif roll_result >= 5:
            Log.create_object(
                game_id,
                f"The assassination attempt succeeded. {target.display_name} was killed!",
            )
        elif is_caught:
            Log.create_object(
                game_id,
                f"The assassination attempt failed. {assassin.display_name} was caught!",
            )
        else:
            Log.create_object(
                game_id,
                f"The assassination attempt had no effect. {target.display_name} survived and the assassin escaped.",
            )

        # --- Apply target consequence ---
        # Capture statuses before kill_senator clears them.
        target_named_in_proposal = target.has_status_item(
            Senator.StatusItem.NAMED_IN_PROPOSAL
        )
        target_was_censor = target.has_title(Senator.Title.CENSOR)
        if roll_result >= 5:
            # Target is killed regardless of whether the assassin was caught —
            # a bodyguard catch reroll does NOT undo the kill.
            kill_senator(target, CauseOfDeath.ASSASSINATION)
            game.refresh_from_db()
            handle_proposal_consequences(
                game, target, target_named_in_proposal, target_was_censor
            )
            game.refresh_from_db()

        # --- Apply caught consequence ---
        # TODO: §1.09.74 Special Major Prosecution is not yet implemented.
        # When added, a guilty verdict should trigger: FL loses 5 influence,
        # mortality chit draws equal to target popularity, and FL death.
        # For now, only the assassin's execution is applied.
        if is_caught:
            kill_senator(assassin, CauseOfDeath.EXECUTION)
            game.refresh_from_db()

        # --- Clean up assassination statuses ---
        self._cleanup(game, list(Senator.objects.filter(game=game_id, alive=True)))

        # --- Return to interrupted sub_phase ---
        game.sub_phase = game.interrupted_sub_phase
        game.interrupted_sub_phase = ""
        game.assassination_roll_result = 0
        game.assassination_roll_modifier = 0
        game.bodyguard_rerolls_remaining = 0
        game.save()

        return True

    def _cleanup(self, game: Game, senators: list) -> None:
        cleanup_statuses = [
            Senator.StatusItem.ASSASSIN,
            Senator.StatusItem.ASSASSINATION_TARGET,
            Senator.StatusItem.CAUGHT,
        ]
        for senator in senators:
            changed = False
            for status in cleanup_statuses:
                if senator.has_status_item(status):
                    senator.remove_status_item(status)
                    changed = True
            if changed:
                senator.save()
