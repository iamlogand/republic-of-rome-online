from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import land_victors_in_declaration_order
from rorapp.models import Game


class CivilWarDeclarationDoneEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.CIVIL_WAR_DECLARATION
            and not land_victors_in_declaration_order(game_state.game.id)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.SECONDARY_REBELS
        game.save()
        return True
