import random
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.resolve_combat import resolve_combat
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
                and c.commander.faction.has_status_item(FactionStatusItem.DONE)
                for c in game_state.campaigns
                if c.commander and c.imminent
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        imminent_campaigns = Campaign.objects.filter(game=game_id, imminent=True)
        potential_attackers = [c.commander for c in imminent_campaigns]
        preferred_attackers = [
            c
            for c in potential_attackers
            if c and c.has_status_item(Senator.StatusItem.PREFERRED_ATTACKER)
        ]
        if not imminent_campaigns.exists() or len(preferred_attackers) == 0:
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

        selected_campaign = [
            c for c in imminent_campaigns if c.commander == selected_attacker
        ][0]

        resolve_combat(game_id, selected_campaign.id, random_resolver)

        # Clean up
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.DONE)
        Faction.objects.bulk_update(factions, ["status_items"])
        for commander in preferred_attackers:
            if Senator.StatusItem.PREFERRED_ATTACKER.value in commander.status_items:
                commander.status_items.remove(
                    Senator.StatusItem.PREFERRED_ATTACKER.value
                )
        Senator.objects.bulk_update(preferred_attackers, ["status_items"])

        # If only one campaign remains imminent, allow it to be resolved normally
        remaining_imminent_campaigns = Campaign.objects.filter(
            game=game_id, imminent=True
        )
        if remaining_imminent_campaigns.count() == 1:
            for campaign in remaining_imminent_campaigns:
                campaign.imminent = False
            Campaign.objects.bulk_update(remaining_imminent_campaigns, ["imminent"])

        return True
