from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.rebel_maintenance import MAINTENANCE_COST, released_legions
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Game, Log


class ReleasedForcesEliminatedEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        legions = released_legions(game_state.game.id)
        return (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REBEL_MAINTENANCE
            and bool(legions)
            and game_state.game.state_treasury < MAINTENANCE_COST * len(legions)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        legions = released_legions(game_id)
        Log.create_object(
            game_id,
            f"The State could not afford {unit_list_to_string(legions, [])} "
            "released by the rebels, and they were eliminated.",
        )
        for legion in legions:
            legion.delete()
        return True
