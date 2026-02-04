from rorapp.classes.random_resolver import RandomResolver
from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game


class InitialPhaseDoneEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.INITIAL
            and game_state.game.sub_phase == Game.SubPhase.FACTION_LEADER
            and all(
                f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        # Remove done status
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.DONE)
        Faction.objects.bulk_update(factions, ["status_items"])

        # Progress game
        game = Game.objects.get(id=game_id)
        game.phase = Game.Phase.MORTALITY
        game.sub_phase = Game.SubPhase.START
        game.save()
        return True
