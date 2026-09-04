from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.helpers.civil_war import land_victors_in_declaration_order
from rorapp.models import Faction, Game


class RevolutionPhaseEndEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.CIVIL_WAR_DECLARATION
            and not land_victors_in_declaration_order(game_state.game.id)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.AWAITING_DECISION)
            faction.remove_status_item(FactionStatusItem.DONE)
        Faction.objects.bulk_update(factions, ["status_items"])

        # Progress game
        game = Game.objects.get(id=game_id)
        game.phase = Game.Phase.MORTALITY
        game.sub_phase = Game.SubPhase.START
        game.turn += 1
        game.save()

        return True
