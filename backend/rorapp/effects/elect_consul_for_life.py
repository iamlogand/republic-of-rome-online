from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_state import clear_proposal_state
from rorapp.helpers.consul_for_life import (
    CONSUL_FOR_LIFE_PREFIX,
    grant_consul_for_life,
)
from rorapp.helpers.motion_result import log_motion_result
from rorapp.helpers.unanimous_defeat import handle_unanimous_defeat
from rorapp.models import Game, Senator


class ElectConsulForLifeEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and not (
                game_state.game.current_proposal is None
                or game_state.game.current_proposal == ""
            )
            and game_state.game.current_proposal.startswith(CONSUL_FOR_LIFE_PREFIX)
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        if not game.current_proposal:
            return False
        senator_name = game.current_proposal[len(CONSUL_FOR_LIFE_PREFIX):]
        senators = Senator.objects.filter(game=game_id, alive=True)
        candidate = next(
            (s for s in senators if s.display_name == senator_name), None
        )

        if game.votes_yea > game.votes_nay:
            log_motion_result(game, passed=True)
            clear_proposal_state(game_id)
            if candidate:
                grant_consul_for_life(game_id, candidate.id, appointed=False)
        else:
            game.add_defeated_proposal(game.current_proposal)
            log_motion_result(game, passed=False)
            game.save()
            handle_unanimous_defeat(game_id)
            clear_proposal_state(game_id)

        return True
