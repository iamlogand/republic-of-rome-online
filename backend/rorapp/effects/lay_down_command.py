from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.lay_down_command import lay_down_command
from rorapp.models import Campaign, Game, War


class LayDownCommandEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.CIVIL_WAR_DECLARATION
            and any(c.land_victory for c in game_state.campaigns)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        campaigns = (
            Campaign.objects.filter(game=game_id, war__status=War.Status.DEFEATED)
            .select_related("commander", "master_of_horse")
            .order_by("id")
        )
        for campaign in campaigns:
            lay_down_command(campaign)
        set_hrao(game_id)
        return True
