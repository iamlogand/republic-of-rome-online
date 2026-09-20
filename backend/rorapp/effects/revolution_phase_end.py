from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.declare_revolt import march_on_rome
from rorapp.helpers.hrao import MAJOR_OFFICES
from rorapp.models import Campaign, Faction, Game, Senator


class RevolutionPhaseEndEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.REVOLT_DECLARATION
            and not any(c.land_victory for c in game_state.campaigns)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
            faction.remove_status_item(FactionStatusItem.DONE)
        Faction.objects.bulk_update(factions, ["status_items"])

        senators = list(Senator.objects.filter(game=game_id, rebel=True))
        for senator in senators:
            if senator.has_status_item(Senator.StatusItem.DECLARED_REVOLT):
                march_on_rome(Campaign.objects.get(game=game_id, commander=senator))
            senator.remove_status_item(Senator.StatusItem.DECLARED_REVOLT)
            # Once the rebels are determined, each loses his offices (1.11.33)
            for office in MAJOR_OFFICES:
                senator.remove_title(office)
        Senator.objects.bulk_update(senators, ["status_items", "titles"])

        rolled = list(
            Senator.objects.filter(
                game=game_id,
                status_items__contains=[Senator.StatusItem.ROLLED_FOR_LEGIONS.value],
            )
        )
        for senator in rolled:
            senator.remove_status_item(Senator.StatusItem.ROLLED_FOR_LEGIONS)
        Senator.objects.bulk_update(rolled, ["status_items"])

        # Progress game
        game = Game.objects.get(id=game_id)
        game.phase = Game.Phase.MORTALITY
        game.sub_phase = Game.SubPhase.START
        game.turn += 1
        game.save()

        return True
