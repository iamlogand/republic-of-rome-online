from django.db.models import Count

from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Campaign, Game, Log, Senator


class SenateEndEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.SENATE
            and game_state.game.sub_phase == Game.SubPhase.END
        )

    def execute(self, game_id: int) -> bool:

        campaigns = (
            Campaign.objects.filter(game=game_id)
            .annotate(
                legion_count=Count("legions", distinct=True),
                fleet_count=Count("fleets", distinct=True),
            )
            .select_related("war", "commander")
        )
        for campaign in campaigns:
            war = campaign.war
            base_log_text = f"{campaign.display_name} was automatically recalled from the {war.name}"

            recall = False

            if war.naval_strength == 0:
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
                        text=base_log_text + " due to insufficient fleet support for the land battle.",
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
                campaign.delete()
                if campaign.commander:
                    commander = campaign.commander
                    commander.location = "Rome"
                    commander.remove_title(Senator.Title.PROCONSUL)
                    commander.save()

        game = Game.objects.get(id=game_id)
        game.phase = Game.Phase.COMBAT
        game.sub_phase = Game.SubPhase.START
        game.save()

        return True
