from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game, Log, War


class MilitaryPhaseEndEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.MILITARY
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)

        # Identify unprosecuted wars
        wars = War.objects.filter(game=game_id, status=War.Status.ACTIVE).order_by(
            "name"
        )
        for war in wars:
            war.status = War.Status.UNPROSECUTED
            war.save()
            Log.create_object(
                game_id,
                f"Rome has not prosecuted the {war.name}.",
            )

        # Progress game
        game.phase = Game.Phase.MORTALITY
        game.sub_phase = Game.SubPhase.START
        game.turn += 1
        game.save()
        return True
