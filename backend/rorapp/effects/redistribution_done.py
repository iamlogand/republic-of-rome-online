from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


class RedistributionDoneEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVENUE
            and game_state.game.sub_phase == Game.SubPhase.REDISTRIBUTION
            and all(
                f.has_status_item(Faction.StatusItem.DONE) for f in game_state.factions
            )
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:

        # Remove done status
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(Faction.StatusItem.DONE)
        Faction.objects.bulk_update(factions, ["status_items"])

        # Remove contributed status
        senators = Senator.objects.filter(game=game_id)
        for senator in senators:
            if senator.has_status_item(Senator.StatusItem.CONTRIBUTED):
                senator.remove_status_item(Senator.StatusItem.CONTRIBUTED)
        Senator.objects.bulk_update(senators, ["status_items"])

        # Progress game
        game = Game.objects.get(id=game_id)
        game.phase = Game.Phase.FORUM
        game.sub_phase = Game.SubPhase.START
        game.save()
        return True
