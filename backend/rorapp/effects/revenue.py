from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Game, Senator


class RevenueEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == "revenue" and game_state.game.sub_phase == "start"
        )

    def execute(self, game_id: int) -> None:

        # Senators earn personal revenue
        senators = Senator.objects.filter(game=game_id, alive=True)
        for senator in senators:
            senator.talents += 1
        Senator.objects.bulk_update(senators, ["talents"])

        # Rome earns revenue
        game = Game.objects.get(id=game_id)
        game.state_treasury += 100

        # Progress game
        game.phase = "revenue"
        game.sub_phase = "redistribution"
        game.save()
