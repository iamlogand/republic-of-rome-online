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
            game=game_id, unprosecuted=True
        ).count()
        unrest_increase = unprosecuted_war_count
        reasons = ""
        if unprosecuted_war_count > 0:
            reasons += f"{unprosecuted_war_count} unprosecuted {'wars' if unprosecuted_war_count > 1 else 'war'}"
        if unrest_increase > 0:
            Log.create_object(
                game_id,
                f"Unrest has increased by {unrest_increase} due to {reasons}.",
            )
        game.unrest += unrest_increase

        # Progress game
        game.phase = Game.Phase.SENATE
        game.sub_phase = Game.SubPhase.START
        game.save()
        return True
