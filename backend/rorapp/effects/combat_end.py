from collections import defaultdict
from typing import List
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.hrao import set_hrao
from rorapp.models import Campaign, Fleet, Game, Legion, Log, Senator, War


class CombatEndEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.COMBAT
            and game_state.game.sub_phase == Game.SubPhase.END
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        game = Game.objects.get(id=game_id)
        wars = War.objects.filter(game=game_id).order_by("id")
        campaigns = Campaign.objects.filter(game=game_id).select_related("commander")
        fleets = Fleet.objects.filter(game=game_id)
        legions = Legion.objects.filter(game=game_id)

        unprosecuted_war_names: List[str] = []

        campaigns_by_war = defaultdict(list)
        for c in campaigns:
            campaigns_by_war[c.war_id].append(c.id)

        for war in wars:

            # Identify unprosecuted wars
            campaign_ids = campaigns_by_war[war.id]
            if len(campaign_ids) > 0:
                surviving_fleets = fleets.filter(campaign__in=campaign_ids).exists()
                surviving_legions = legions.filter(campaign__in=campaign_ids).exists()
            else:
                surviving_fleets = surviving_legions = False
            if war.status == War.Status.ACTIVE and not (
                (war.fought_naval_battle and surviving_fleets)
                or (war.fought_land_battle and surviving_legions)
            ):
                war.unprosecuted = True
                unprosecuted_war_names.append(war.name)

            # Reset turn states
            war.reset_turn_states()

            war.save()

        # Log unprosecuted wars
        count = len(unprosecuted_war_names)
        if count > 0:
            log_text = "Rome has allowed the "
            for i in range(count):
                log_text += unprosecuted_war_names[i]
                if i < count - 2:
                    log_text += ", the "
                elif i == count - 2:
                    log_text += " and the "
            log_text += " to be unprosecuted."
            Log.create_object(game_id, log_text)

        # Identify proconsuls
        new_proconsuls = []
        for campaign in campaigns:
            campaign.recently_deployed = False
            campaign.recently_reinforced = False
            commander = campaign.commander
            if commander and not commander.has_title(Senator.Title.PROCONSUL):
                commander.add_title(Senator.Title.PROCONSUL)
                commander.add_title(Senator.Title.PRIOR_CONSUL)
                commander.remove_title(Senator.Title.ROME_CONSUL)
                commander.remove_title(Senator.Title.FIELD_CONSUL)
                new_proconsuls.append(commander)
        if len(new_proconsuls) > 0:
            Senator.objects.bulk_update(new_proconsuls, ["titles"])
        if len(campaigns) > 0:
            Campaign.objects.bulk_update(
                campaigns, ["recently_deployed", "recently_reinforced"]
            )

        # Set HRAO
        set_hrao(game_id)

        # Progress game
        game.phase = Game.Phase.MORTALITY
        game.sub_phase = Game.SubPhase.START
        game.turn += 1
        game.save()
        return True
