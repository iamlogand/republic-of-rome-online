from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.rebel_maintenance import (
    payable_rebel_legions,
    rebel_faction,
    released_legions,
)
from rorapp.models import Faction, Game


class RebelMaintenanceDoneEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if not (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REBEL_MAINTENANCE
        ):
            return False
        if released_legions(game_state.game.id):
            return False
        faction = rebel_faction(game_state.game.id)
        if not faction or not payable_rebel_legions(game_state.game.id):
            return True
        return faction.has_status_item(FactionStatusItem.DONE)

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.DONE)
        Faction.objects.bulk_update(factions, ["status_items"])

        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.REDISTRIBUTION
        game.save()
        return True
