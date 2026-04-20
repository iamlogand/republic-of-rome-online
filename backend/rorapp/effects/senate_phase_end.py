from django.db.models import Count

from rorapp.classes.concession import Concession
from rorapp.classes.game_effect_item import GameEffect
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.text import to_sentence_case
from rorapp.models import Campaign, Game, Log, Senator


class SenatePhaseEndEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.END
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        campaigns = (
            Campaign.objects.filter(game=game_id)
            .annotate(
                legion_count=Count("legions", distinct=True),
                fleet_count=Count("fleets", distinct=True),
            )
            .select_related("war", "commander", "master_of_horse")
        )
        for campaign in campaigns:
            war = campaign.war
            base_log_text = f"{to_sentence_case(campaign.display_name)} was automatically recalled from the {war.name}"

            recall = False

            if campaign.commander is None:
                recall = True
                Log.create_object(
                    game_id=game_id,
                    text=base_log_text + " because there was no commander.",
                )
            elif war.naval_strength == 0:
                if campaign.legion_count == 0:
                    recall = True
                    Log.create_object(
                        game_id=game_id,
                        text=base_log_text
                        + " because no legions were present for the land battle.",
                    )

                elif campaign.fleet_count < war.fleet_support:
                    recall = True
                    Log.create_object(
                        game_id=game_id,
                        text=base_log_text
                        + " due to insufficient fleet support for the land battle.",
                    )
            else:
                if campaign.fleet_count == 0:
                    recall = True
                    Log.create_object(
                        game_id=game_id,
                        text=base_log_text
                        + " because no fleets were present for the naval battle.",
                    )

            if recall:
                master_of_horse = campaign.master_of_horse
                campaign.delete()
                if campaign.commander:
                    commander = campaign.commander
                    commander.location = "Rome"
                    commander.remove_title(Senator.Title.PROCONSUL)
                    commander.save()
                if master_of_horse:
                    master_of_horse.location = "Rome"
                    master_of_horse.save()

        senators = Senator.objects.filter(game=game_id)
        for senator in senators:
            senator.remove_status_item(Senator.StatusItem.STEPPED_DOWN)
        Senator.objects.bulk_update(senators, ["status_items"])

        game = Game.objects.get(id=game_id)

        no_active_bills = (
            game.count_effect(GameEffect.LAND_BILL_1) == 0
            and game.count_effect(GameEffect.LAND_BILL_2) == 0
            and game.count_effect(GameEffect.LAND_BILL_3) == 0
        )
        if no_active_bills:
            for senator in Senator.objects.filter(game=game_id):
                if senator.has_concession(Concession.LAND_COMMISSIONER):
                    senator.remove_concession(Concession.LAND_COMMISSIONER)
                    senator.save()
                    game.add_concession(Concession.LAND_COMMISSIONER)
                    Log.create_object(
                        game_id,
                        f"The {Concession.LAND_COMMISSIONER.value} concession was returned to the Forum as no land bill is in effect.",
                    )

        game.phase = Game.Phase.COMBAT
        game.sub_phase = Game.SubPhase.START
        game.clear_senate_sub_phase_proposals()
        game.save()

        return True
