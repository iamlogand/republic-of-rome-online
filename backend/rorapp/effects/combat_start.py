from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Campaign, Game


class CombatStartEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int) -> bool:
        game = Game.objects.get(id=game_id)
        campaigns = Campaign.objects.filter(game=game.id).order_by("id")
        
        # Set campaigns to pending
        for campaign in campaigns:
            campaign.pending = True
        Campaign.objects.bulk_update(campaigns, ["pending"])

        # Progress game
        game.sub_phase = Game.SubPhase.RESOLUTION
        game.save()
        return True
