from django.utils.timezone import now
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.rebel_end_game import active_wars_against_rome
from rorapp.models import Game, Log, War


class GameOverMilitaryOverwhelmedEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.END
            and len(active_wars_against_rome(game_state.game.id)) > 3
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        game = Game.objects.get(id=game_id)
        game.finished_on = now()
        game.save()

        active_war_count = len(active_wars_against_rome(game_id))

        Log.create_object(
            game.id,
            f"Game over! The military was overwhelmed by {active_war_count} simultaneous wars, leading to the sack of Rome and the collapse of the Republic.",
        )

        return True
