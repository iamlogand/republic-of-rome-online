from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.hrao import set_new_hrao
from rorapp.helpers.kill_senator import kill_senator
from rorapp.helpers.mortality_chits import draw_mortality_chits
from rorapp.models import Faction, Game, Log, Senator


class MortalityEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.MORTALITY
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int) -> None:

        game = Game.objects.get(id=game_id)

        # Kill senators
        senators = Senator.objects.filter(game=game_id, alive=True)
        codes = draw_mortality_chits()
        codes = [18]  # TEMPORARY - DO NOT COMMIT
        for code in codes:
            victims = senators.filter(code=code)  # There should be 0 or 1 victims
            if victims.exists():
                victim = victims.first()
                if victim and victim.faction:
                    faction = Faction.objects.get(id=victim.faction.id)
                    was_hrao = victim.has_title(Senator.Title.HRAO)
                    kill_senator(game_id, victim.id)
                    Log.objects.create(
                        game=game,
                        text=f"{victim.display_name} of {faction.display_name} died of natural causes.",
                    )
                    if was_hrao:
                        set_new_hrao(game_id)

        # Progress game
        game = Game.objects.get(id=game_id)
        game.phase = Game.Phase.REVENUE
        game.sub_phase = Game.SubPhase.START
        game.turn += 1
        game.save()
