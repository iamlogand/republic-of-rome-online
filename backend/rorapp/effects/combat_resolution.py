from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.resolve_combat import resolve_combat
from rorapp.models import Campaign, Game, War


class CombatResolutionEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.RESOLUTION
            and not any(c.imminent for c in game_state.campaigns)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        campaigns = Campaign.objects.filter(game=game.id).order_by("id")
        wars = War.objects.filter(game=game.id).order_by("id")

        # Identify wars in order of resolution
        last_campaigns = []
        for war in wars:
            last_campaign = campaigns.filter(war=war).last()
            if last_campaign:
                last_campaigns.append(last_campaign)
        ordered_last_campaigns = sorted(last_campaigns, key=lambda c: c.id)
        ordered_wars = []
        for campaign in ordered_last_campaigns:
            ordered_wars.append(campaign.war)

        # Resolve battles
        for war in ordered_wars:
            pending_campaigns = Campaign.objects.filter(
                game=game_id, war=war, pending=True
            )
            if len(pending_campaigns) == 0:
                continue

            if len(pending_campaigns) == 1:
                current_campaign = pending_campaigns.first()
                if not current_campaign:
                    return False

                resolve_combat(game.id, current_campaign.id, random_resolver)
            else:
                for campaign in pending_campaigns:
                    campaign.imminent = True
                Campaign.objects.bulk_update(pending_campaigns, ["imminent"])
                return True  # Exit so commanders can determine resolution order before progressing

        # Progress game
        game.refresh_from_db()
        game.sub_phase = Game.SubPhase.END
        game.save()
        return True
