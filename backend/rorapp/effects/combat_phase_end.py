from django.db.models import Count
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Campaign, Game, Log, War


class CombatPhaseEndEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.START
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)

        # Identify unprosecuted wars
        unprosecuted_wars = (
            War.objects.filter(game=game, status=War.Status.ACTIVE)
            .annotate(campaign_count=Count("campaigns"))
            .filter(campaign_count=0)
            .order_by("id")
        )
        for war in unprosecuted_wars:
            war.unprosecuted = True
            war.save()
            Log.create_object(
                game_id,
                f"Rome has not prosecuted the active war: {war.name}.",
            )

        # Progress game
        game.phase = Game.Phase.MORTALITY
        game.sub_phase = Game.SubPhase.START
        game.turn += 1
        game.save()
        return True
