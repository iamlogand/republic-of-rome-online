from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.assassination_participants import (
    get_assassination_participants,
    is_land_bill_assassination,
)
from rorapp.helpers.assassination_proposal_consequences import (
    apply_proposal_consequences,
    death_record,
)
from rorapp.helpers.kill_senator import CauseOfDeath, kill_senator
from rorapp.helpers.resume_interrupted_sub_phase import resume_interrupted_sub_phase
from rorapp.helpers.special_major_prosecution import punish_caught_assassin
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
        target_name = target.display_name
        target_popularity = target.popularity
        # Read before the target dies, since his death leaves one sponsor named
        land_bill_attempt = is_land_bill_assassination(game)

        # Log the outcome now that bodyguards have had their chance
        if roll_result >= 5 and is_caught:
            Log.create_object(
                game_id,
                f"The assassination attempt succeeded and {target.display_name} was killed, but {assassin.display_name} was caught!",
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

        if roll_result >= 5:
            # Target is killed regardless of whether the assassin was caught —
            # a bodyguard catch reroll does NOT undo the kill.
            target_death = death_record(target)
            kill_senator(target, CauseOfDeath.ASSASSINATION)
            apply_proposal_consequences(game_id, [target_death])
            game.refresh_from_db()

        # Clean up assassination statuses before the punishment, so that they are
        # not carried into a special major prosecution
        self._cleanup(game, list(Senator.objects.filter(game=game_id, alive=True)))

        # Apply caught consequence (1.09.74)
        if is_caught:
            assassin.refresh_from_db()
            punish_caught_assassin(
                game_id,
                assassin,
                target_name,
                target_popularity,
                random_resolver,
                spare_faction=land_bill_attempt,
            )

        resume_interrupted_sub_phase(game_id)

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
