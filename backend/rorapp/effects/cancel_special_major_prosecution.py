from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.special_major_prosecution import (
    conclude_special_major_prosecution,
    current_prosecution,
    log_prosecution_cancelled,
)
from rorapp.models import Game, Senator


class CancelSpecialMajorProsecutionEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        # An assassination may be attempted during a trial (1.09.7), so the
        # accused can be killed before the senate reaches a verdict
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase
            == Game.SubPhase.SPECIAL_MAJOR_PROSECUTION
            and bool(game_state.game.special_major_prosecutions)
            and not any(
                s.has_status_item(Senator.StatusItem.ACCUSED)
                for s in game_state.senators
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        trial = current_prosecution(game)
        if trial is None:
            return False

        log_prosecution_cancelled(game_id, trial)
        conclude_special_major_prosecution(game_id, [])

        return True
