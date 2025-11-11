import random
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.clear_proposal_and_votes import clear_proposal_and_votes
from rorapp.helpers.transfer_power_consuls import transfer_power_consuls
from rorapp.models import Campaign, Faction, Game, Senator
from rorapp.models.log import Log


class PreferredAttackerEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.RESOLUTION
            and any(c.imminent for c in game_state.campaigns)
            and any(
                s.has_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
                for s in game_state.senators
                if s.alive
            )
            and all(
                c.commander.faction
                and c.commander.faction.has_status_item(Faction.StatusItem.DONE)
                for c in game_state.campaigns
                if c.imminent
            )
        )

    def execute(self, game_id: int) -> bool:
        imminent_campaigns = [
            c for c in Campaign.objects.filter(game=game_id) if c.imminent
        ]
        potential_attackers = [c.commander for c in imminent_campaigns]
        preferred_attackers = [
            c
            for c in potential_attackers
            if c.has_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
        ]
        if len(preferred_attackers) == 0:
            return False

        war = imminent_campaigns[0].war
        if len(preferred_attackers) == 1:
            selected_attacker = preferred_attackers[0]
            Log.create_object(
                game_id,
                f"Commanders agreed for {selected_attacker.display_name} to attack the {war.name}.",
            )
        else:
            selected_attacker = random.choice(preferred_attackers)
            Log.create_object(
                game_id,
                f"Commanders disagreed on who should attack the {war.name}. After casting lots, fate chose {selected_attacker.display_name}.",
            )

        selected_campaign = [c for c in imminent_campaigns if c.commander == selected_attacker][0]
        
        # TODO: resolve combat
        selected_campaign.pending = False
        selected_campaign.save()

        # Clean up
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(Faction.StatusItem.DONE)
        Faction.objects.bulk_update(factions, ["status_items"])
        for commander in preferred_attackers:
            commander.remove_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
        Senator.objects.bulk_update(preferred_attackers, ["status_items"])
        if len(imminent_campaigns) <= 2:
            for campaign in imminent_campaigns:
                campaign.imminent = False
            Campaign.objects.bulk_update(imminent_campaigns, ["imminent"])

        return True
