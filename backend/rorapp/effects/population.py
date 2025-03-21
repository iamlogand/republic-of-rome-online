from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game, Log, War


class PopulationEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.POPULATION
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)

        # Increase unrest
        unprosecuted_war_count = War.objects.filter(
            game=game_id, status=War.Status.UNPROSECUTED
        ).count()
        if unprosecuted_war_count > 0:
            Log.create_object(
                game_id,
                f"Unrest has increased due to {unprosecuted_war_count} unprosecuted war{'s' if unprosecuted_war_count > 1 else ''}.",
            )
        game.unrest += unprosecuted_war_count

        # Progress game
        game.phase = Game.Phase.MORTALITY
        game.sub_phase = Game.SubPhase.START
        game.turn += 1
        game.save()
        return True
