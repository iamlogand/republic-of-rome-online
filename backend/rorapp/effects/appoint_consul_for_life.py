from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.consul_for_life import (
    get_consul_for_life_appointee,
    grant_consul_for_life,
)


class AppointConsulForLifeEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if game_state.game.consul_for_life_appointed:
            return False
        return get_consul_for_life_appointee(game_state.senators) is not None

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        snapshot = GameStateSnapshot(game_id)
        appointee = get_consul_for_life_appointee(snapshot.senators)
        if appointee is None:
            return False
        grant_consul_for_life(game_id, appointee.id, appointed=True)
        return True
