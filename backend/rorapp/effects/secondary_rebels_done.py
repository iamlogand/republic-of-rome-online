from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import (
    apply_rebel_markers,
    desert_to_the_primary_rebel,
    get_civil_war,
    refresh_civil_war_strength,
    relinquish_command,
    undecided_secondary_rebels,
)
from rorapp.helpers.hrao import set_hrao
from rorapp.helpers.unit_lists import unit_list_to_string
from rorapp.models import Campaign, Game, Log, Senator


class SecondaryRebelsDoneEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.SECONDARY_REBELS
            and not undecided_secondary_rebels(game_state.game.id)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        war = get_civil_war(game_id)
        if war and war.primary_rebel:
            rebel_campaign = Campaign.objects.filter(
                game=game_id, commander=war.primary_rebel
            ).first()

            # A Master of Horse who did not join the revolt returns to Rome (1.11.32)
            if rebel_campaign and rebel_campaign.master_of_horse:
                master_of_horse = rebel_campaign.master_of_horse
                if not master_of_horse.rebel:
                    master_of_horse.location = "Rome"
                    master_of_horse.save()
                    rebel_campaign.master_of_horse = None
                    rebel_campaign.save()
                    Log.create_object(
                        game_id,
                        f"{master_of_horse.display_name} refused to follow the "
                        "revolt and returned to Rome.",
                    )

            rebels = list(Senator.objects.filter(game=game_id, rebel=True))
            for rebel in rebels:
                if rebel.id != war.primary_rebel.id:
                    relinquish_command(rebel)
            for rebel in rebels:
                rebel.refresh_from_db()
                apply_rebel_markers(rebel)

            deserters = desert_to_the_primary_rebel(game_id)
            if deserters:
                Log.create_object(
                    game_id,
                    f"{unit_list_to_string(deserters, [])} deserted to "
                    f"{war.primary_rebel.display_name}.",
                )

            refresh_civil_war_strength(game_id)
            set_hrao(game_id)

        senators = Senator.objects.filter(game=game_id)
        for senator in senators:
            senator.remove_status_item(Senator.StatusItem.REMAINED_LOYAL)
            senator.remove_status_item(Senator.StatusItem.ROLLED_FOR_LEGIONS)
        Senator.objects.bulk_update(senators, ["status_items"])

        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.END
        game.save()
        return True
