from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.text import format_list
from rorapp.models import EnemyLeader, Game, Log, Senator


class PuttingRomeInOrderEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.PUTTING_ROME_IN_ORDER
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)

        dead_senator_list = list(
            Senator.objects.filter(game=game_id, alive=False, family=True)
        )

        for senator in dead_senator_list:
            roll = random_resolver.roll_dice()
            if roll >= 5:
                previous_name = (
                    f"{senator.display_name}'"
                    if senator.display_name.endswith("s")
                    else f"{senator.display_name}'s"
                )
                senator.generation += 1
                senator.alive = True
                senator.save()
                Log.create_object(
                    game_id,
                    f"{previous_name} heir {senator.display_name} appeared as an unaligned senator.",
                )

        inactive_leaders = list(EnemyLeader.objects.filter(game=game_id, active=False))
        dead_leaders = []
        for leader in inactive_leaders:
            roll = random_resolver.roll_dice()
            if roll >= 5:
                dead_leaders.append(leader.name)
                leader.delete()
        if dead_leaders:
            Log.create_object(
                game_id,
                f"Enemy leader{' ' if len(dead_leaders) == 1 else 's '}{format_list(dead_leaders)} died.",
            )

        if game.era_ends:
            game.sub_phase = Game.SubPhase.ERA_ENDS
        else:
            game.phase = Game.Phase.POPULATION
            game.sub_phase = Game.SubPhase.START
        game.save()
        return True
