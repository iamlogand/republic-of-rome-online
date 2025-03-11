from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.kill_senator import kill_senator
from rorapp.helpers.mortality_chits import draw_mortality_chits
from rorapp.models import Game, Senator, Log


class MortalityEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.MORTALITY
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)

        # Kill senators
        deaths = 0
        senators = Senator.objects.filter(game=game_id, alive=True)
        codes = draw_mortality_chits()
        for code in codes:
            victims = senators.filter(
                code=code
            )  # There should be 0 or 1 victims for each code
            if victims.exists():
                victim = victims.first()
                if victim and victim.faction:
                    kill_senator(game_id, victim.id)
                    deaths += 1

        if deaths == 0:
            Log.create_object(
                game_id,
                "All senators have survived the mortality phase.",
            )

        # Progress game
        game = Game.objects.get(id=game_id)
        game.phase = Game.Phase.REVENUE
        game.sub_phase = Game.SubPhase.START
        game.save()
        return True
