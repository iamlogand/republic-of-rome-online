from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.game_data import get_senator_codes
from rorapp.helpers.kill_senator import kill_senator
from rorapp.helpers.text import format_list
from rorapp.models import Game, Senator, Log, War
from rorapp.models.enemy_leader import EnemyLeader


class MortalityEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.MORTALITY
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
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
                message = f"The {war.name} has become active."

                inactive_leaders = list(
                    EnemyLeader.objects.filter(
                        game=game_id, series_name=war.series_name, active=False
                    )
                )
                if bool(inactive_leaders):
                    for leader in inactive_leaders:
                        leader.active = True
                        leader.save()
                    leaders_text = format_list([l.name for l in inactive_leaders])
                    message += f" The war is joined by {leaders_text}."
                Log.create_object(game_id, message)

        # Kill senators
        deaths = 0
        senators = Senator.objects.filter(game=game_id, alive=True)
        codes = random_resolver.draw_mortality_chits()
        for code in codes:
            victims = [s for s in senators if get_senator_codes(s.code)[0] == str(code)]
            if victims:
                victim = victims[0]
                if victim:
                    kill_senator(victim)
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
