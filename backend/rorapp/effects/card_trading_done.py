from rorapp.classes.faction_status_item import FactionStatusItem
from rorapp.classes.random_resolver import RandomResolver
from rorapp.effects.meta.effect_base import EffectBase
from rorapp.game_state.game_state_snapshot import GameStateSnapshot
from rorapp.models import Faction, Game, Senator


class CardTradingDoneEffect(EffectBase):

    def validate(self, game_state: GameStateSnapshot) -> bool:
        return (
            game_state.game.phase == Game.Phase.REVOLUTION
            and game_state.game.sub_phase == Game.SubPhase.CARD_TRADING
            and all(f.has_status_item(FactionStatusItem.DONE) for f in game_state.factions)
        )

    def execute(self, game_id: int, random_resolver: RandomResolver) -> bool:
        factions = Faction.objects.filter(game=game_id)
        for faction in factions:
            faction.remove_status_item(FactionStatusItem.DONE)
            if any(
                s.has_title(Senator.Title.HRAO)
                for s in Senator.objects.filter(game=game_id, faction=faction.id, alive=True)
            ):
                faction.add_status_item(FactionStatusItem.AWAITING_DECISION)
        Faction.objects.bulk_update(factions, ["status_items"])

        game = Game.objects.get(id=game_id)
        game.sub_phase = Game.SubPhase.PLAY_STATESMEN_CONCESSIONS
        game.save()
        return True
