from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import standing_rebel
from rorapp.helpers.rebel_end_game import BATTLE_WON
from rorapp.models import Game, Log, Senator


class RebelUnopposedEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.RESOLUTION
            and not game_state.game.rebel_winning_condition
        ):
            return False
        civil_war = next((w for w in game_state.wars if w.primary_rebel_id), None)
        if not civil_war:
            return False
        if any(c.war_id == civil_war.id for c in game_state.campaigns):
            return False
        return not any(
            c.pending or c.imminent for c in game_state.campaigns
        ) and not any(
            s.has_status_item(Senator.StatusItem.CONSIDERING_LAND_BATTLE)
            for s in game_state.senators
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        rebel = standing_rebel(game_id)
        game = Game.objects.get(id=game_id)
        game.rebel_winning_condition = BATTLE_WON
        game.save()
        Log.create_object(
            game_id,
            f"The Senate sent no army against {rebel.display_name if rebel else 'the rebels'}, "
            "so his march on Rome went unopposed.",
        )
        return True
