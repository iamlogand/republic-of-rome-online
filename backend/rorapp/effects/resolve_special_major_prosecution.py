from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.motion_result import log_motion_result
from rorapp.helpers.special_major_prosecution import (
    conclude_special_major_prosecution,
    convict,
)
from rorapp.models import Game, Senator


class ResolveSpecialMajorProsecutionEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase
            == Game.SubPhase.SPECIAL_MAJOR_PROSECUTION
            and bool(game_state.game.current_proposal)
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        accused = next(
            (
                s
                for s in Senator.objects.filter(game=game_id)
                if s.has_status_item(Senator.StatusItem.ACCUSED)
            ),
            None,
        )
        if accused is None:
            return False

        guilty = game.votes_yea > game.votes_nay
        log_motion_result(game, passed=guilty)

        deaths = convict(game_id, accused, random_resolver) if guilty else []
        conclude_special_major_prosecution(game_id, deaths)

        return True
