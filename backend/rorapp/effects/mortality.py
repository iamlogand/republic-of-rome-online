from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.kill_senator import kill_senator
from rorapp.helpers.mortality_chits import draw_mortality_chits
from rorapp.models import Game, Senator, Log, War


class MortalityEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.MORTALITY
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)

        # Activate any imminent wars
        wars = War.objects.filter(game=game_id, status=War.Status.IMMINENT).order_by(
            "index"
        )
        activated_series_names = []
        for war in wars:
            if war.series_name not in activated_series_names:
                war.status = War.Status.ACTIVE
                war.save()
                activated_series_names.append(war.series_name)
                Log.create_object(game_id, f"The {war.name} has become active.")

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
