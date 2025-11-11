from typing import List
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Campaign, Game, Log, War


class CombatEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.COMBAT
            and (game_state.game.sub_phase == Game.SubPhase.START or game_state.game.sub_phase == Game.SubPhase.RESOLUTION)
            and not any(c.imminent for c in game_state.campaigns)
        )

    def execute(self, game_id: int) -> bool:

        game = Game.objects.get(id=game_id)
        campaigns = Campaign.objects.filter(game=game.id).order_by("id")
    
        # Set campaigns to pending
        if game.sub_phase == Game.SubPhase.START:
            for campaign in campaigns:
                campaign.pending = True
            Campaign.objects.bulk_update(campaigns, ["pending"])

        # Identify wars in order of resolution
        wars = War.objects.filter(game=game.id).order_by("id")
        unprosecuted_wars: List[War] = []
        last_campaigns = []
        for war in wars:
            last_campaign = campaigns.filter(war=war).last()
            if last_campaign:
                last_campaigns.append(last_campaign)
            else:
                unprosecuted_wars.append(war)
        ordered_last_campaigns = sorted(last_campaigns, key=lambda c: c.id)
        ordered_wars = []
        for campaign in ordered_last_campaigns:
            ordered_wars.append(campaign.war)

        # Handle unprosecuted wars
        if game.sub_phase == Game.SubPhase.START:
            for war in unprosecuted_wars:
                war.unprosecuted = True
                war.save()
                Log.create_object(
                    game_id,
                    f"Rome has not prosecuted the active war: {war.name}.",
                )
            game.sub_phase = Game.SubPhase.RESOLUTION
            game.save()

        # Resolve battles
        for war in ordered_wars:
            pending_campaigns = campaigns.filter(war=war, pending=True)
            if len(pending_campaigns) == 0:
                continue

            if len(pending_campaigns) == 1:
                current_campaign = pending_campaigns.first()
                if not current_campaign:
                    return False

                # TODO: resolve combat
                current_campaign.pending = False
                current_campaign.save()
            else:
                for campaign in pending_campaigns:
                    campaign.imminent = True
                Campaign.objects.bulk_update(pending_campaigns, ["imminent"])
                return True  # Exit so commanders can determine resolution order before progressing

        # Progress game
        game.phase = Game.Phase.MORTALITY
        game.sub_phase = Game.SubPhase.START
        game.turn += 1
        game.save()
        return True
