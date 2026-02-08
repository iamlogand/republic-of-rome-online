from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game


class RevolutionEndEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
        ):
            return all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
        return False

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.MAKING_DECISION)
        Faction.objects.bulk_update(factions, ["status_items"])
        
        # Progress game
        game = Game.objects.get(id=game_id)
        game.phase = Game.Phase.MORTALITY
        game.sub_phase = Game.SubPhase.START
        game.turn += 1
        game.save()
        
        return True
