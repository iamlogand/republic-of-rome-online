from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game, Log, Senator


class PuttingRomeInOrderEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PUTTING_ROME_IN_ORDER
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)

        dead_senators = Senator.objects.filter(
            game=game_id, alive=False, family=True
        )

        for senator in dead_senators:
            roll = random_resolver.roll_dice()
            if roll >= 5:
                senator.generation += 1
                senator.alive = True
                senator.save()
                Log.create_object(
                    game_id,
                    f"{senator.display_name} has entered the forum as an unaligned senator (rolled {roll}).",
                )
            else:
                Log.create_object(
                    game_id,
                    f"{senator.display_name} remained in the curia (rolled {roll}).",
                )

        if not dead_senators.exists():
            Log.create_object(game_id, "There are no senators in the curia.")

        game.phase = Game.Phase.POPULATION
        game.sub_phase = Game.SubPhase.START
        game.save()
        return True
