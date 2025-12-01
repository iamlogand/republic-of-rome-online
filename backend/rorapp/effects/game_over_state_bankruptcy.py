from django.utils.timezone import now
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game, Log


class GameOverStateBankruptcyEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            not (
                game_state.game.phase == Game.Phase.REVENUE
                and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
            )
            and game_state.game.state_treasury < 0
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        game.finished_on = now()
        game.save()

        Log.create_object(
            game.id,
            "Game over! The State Treasury fell into bankruptcy. With no means to sustain her obligations, the Republic collapsed.",
        )

        return True
