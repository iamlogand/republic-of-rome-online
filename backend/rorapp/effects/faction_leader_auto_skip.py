from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game


class FactionLeaderAutoSkipEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        if (
            game_state.game.phase == Game.Phase.FORUM
            and game_state.game.sub_phase == Game.SubPhase.FACTION_LEADER
        ):
            for faction in game_state.factions:
                if faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE):
                    # A faction that has lost every senator has nobody to lead (1.05.4)
                    return not any(
                        s.faction and s.faction.id == faction.id and s.alive
                        for s in game_state.senators
                    )
        return False

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        # End initiative
        for faction in Faction.objects.filter(game=game_id):
            if faction.has_status_item(FactionStatusItem.CURRENT_INITIATIVE):
                faction.remove_status_item(FactionStatusItem.CURRENT_INITIATIVE)
                faction.save()

        # Progress game
        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.END
        game.save()
        return True
