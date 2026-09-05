from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.rebel_end_game import REPUBLIC_COLLAPSED
from rorapp.models import Game, Log


class RebelWinsOnCollapseEffect(EffectBase):

    # Bankruptcy while a senator is in revolt is his win, not everyone's loss (1.12.2)
    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            not (
                game_state.game.phase == Game.Phase.REVENUE
                and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
            )
            and game_state.game.state_treasury < 0
            and not game_state.game.rebel_winning_condition
            and any(s.rebel and s.alive for s in game_state.senators)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        game.rebel_winning_condition = REPUBLIC_COLLAPSED
        game.save()
        Log.create_object(
            game_id,
            "The State Treasury fell into bankruptcy while Rome was in revolt.",
        )
        return True
